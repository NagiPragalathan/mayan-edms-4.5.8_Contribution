from contextlib import contextmanager
import logging

from django.apps import apps
from django.core.files.base import ContentFile
from django.db.models import F, Sum
from django.template.defaultfilters import filesizeformat
from django.utils.functional import cached_property
from django.utils.text import format_lazy
from django.utils.translation import ugettext_lazy as _

from mayan.apps.events.decorators import method_event
from mayan.apps.events.event_managers import EventManagerMethodAfter
from mayan.apps.lock_manager.backends.base import LockingBackend
from mayan.apps.lock_manager.decorators import (
    acquire_lock_class_method, release_lock_class_method, locked_class_method
)
from mayan.apps.lock_manager.exceptions import LockError
from mayan.apps.storage.classes import DefinedStorage

from .events import event_cache_partition_purged, event_cache_purged
from .exceptions import FileCachingException
from .settings import (
    setting_maximum_failed_prune_attempts,
    setting_maximum_normal_prune_attempts
)

logger = logging.getLogger(name=__name__)


class CacheBusinessLogicMixin:
    def get_files(self):
        CachePartitionFile = apps.get_model(
            app_label='file_caching', model_name='CachePartitionFile'
        )

        return CachePartitionFile.objects.filter(
            partition__cache__id=self.pk
        )

    def get_maximum_size_display(self):
        return filesizeformat(bytes_=self.maximum_size)

    get_maximum_size_display.help_text = _(
        'Size at which the cache will start deleting old entries.'
    )
    get_maximum_size_display.short_description = _('Maximum size')

    def get_defined_storage(self):
        try:
            return DefinedStorage.get(name=self.defined_storage_name)
        except KeyError:
            return DefinedStorage(
                dotted_path='', label=_('Unknown'), name='unknown'
            )

    def get_partition_count(self):
        CachePartition = apps.get_model(
            app_label='file_caching', model_name='CachePartition'
        )

        return CachePartition.objects.filter(cache=self).count()

    get_partition_count.short_description = _('Partition count')
    get_partition_count.help_text = _('Total cached objects.')

    def get_partition_file_count(self):
        return self.get_files().count()

    get_partition_file_count.short_description = _('Partition file count')
    get_partition_file_count.help_text = _('Total cached files.')

    def get_total_size(self):
        """
        Return the actual usage of the cache.
        """
        return self.get_files().aggregate(
            file_size__sum=Sum('file_size')
        )['file_size__sum'] or 0

    def get_total_size_display(self):
        total_size = self.get_total_size()

        return format_lazy(
            '{} ({:0.1f}%)', filesizeformat(
                bytes_=total_size
            ), total_size / self.maximum_size * 100
        )

    get_total_size_display.short_description = _('Current size')
    get_total_size_display.help_text = _('Current size of the cache.')

    @cached_property
    def label(self):
        return self.get_defined_storage().label

    def prune(self):
        """
        Deletes files until the total size of the cache is below the allowed
        maximum size of the cache.
        """
        failed_attempts = 0
        normal_attempts = 0
        file_index = 0

        CachePartitionFile = apps.get_model(
            app_label='file_caching', model_name='CachePartitionFile'
        )

        while self.get_total_size() >= self.maximum_size:
            cache_partition_file_queryset = self.get_files().order_by(
                'hits', 'datetime'
            )

            try:
                cache_partition_file = cache_partition_file_queryset[file_index]
            except IndexError:
                # Attempted to get a file beyond what the queryset provided.
                file_index = 0
            else:
                try:
                    cache_partition_file.delete()
                except CachePartitionFile.DoesNotExist:
                    # The file selected from deletion was deleted by another
                    # process before the lock was acquired.
                    file_index += 1
                except LockError:
                    logger.debug(
                        'Lock error trying to delete file "%s" for '
                        'prune. Skipping and attempting next file.',
                        cache_partition_file
                    )
                    failed_attempts += 1
                    file_index += 1

                    if failed_attempts > setting_maximum_failed_prune_attempts.value:
                        raise FileCachingException(
                            'Too many cache prune attempts failed.'
                        )
                else:
                    file_index = 0
                    normal_attempts += 1

                    if normal_attempts > setting_maximum_normal_prune_attempts.value:
                        raise FileCachingException(
                            'Too many cache prunes trying to create a '
                            'single new file.'
                        )

    @method_event(
        event=event_cache_purged,
        event_manager_class=EventManagerMethodAfter,
        target='self'
    )
    def purge(self, user):
        """
        Deletes the entire cache.
        """
        self._event_actor = user

        try:
            DefinedStorage.get(name=self.defined_storage_name)
        except KeyError:
            """
            Unknown or deleted storage. Must not be purged otherwise only
            the database data will be erased but the actual storage files
            will remain.
            """
        else:
            for partition in self.partitions.all():
                partition._event_action_object = self
                try:
                    partition.purge(user=user)
                except Exception as exception:
                    logger.error(
                        'Unable to purge partition ID: %d; %s',
                        partition.pk, exception
                    )
                    # Don't raise exceptions to allow the loop to continue and
                    # avoid a single exception from stoping the purge.

    @cached_property
    def storage(self):
        return self.get_defined_storage().get_storage_instance()


class CachePartitionBusinessLogicMixin:
    @staticmethod
    def get_combined_filename(parent, filename):
        return '{}-{}'.format(parent, filename)

    def _lock_manager_get_lock_name(self, filename):
        return self.get_file_lock_name(filename=filename)

    @contextmanager
    def create_file(self, filename):
        lock_name = self.get_file_lock_name(filename=filename)
        try:
            logger.debug('trying to acquire lock: %s', lock_name)
            lock = LockingBackend.get_backend().acquire_lock(name=lock_name)
            logger.debug('acquired lock: %s', lock_name)
            try:
                self.cache.prune()

                # Since open "wb+" doesn't create files, force the creation
                # of an empty file.
                try:
                    self.cache.storage.delete(
                        name=self.get_full_filename(filename=filename)
                    )
                except Exception as exception:
                    """
                    Some S3 implementations like Google Cloud Storage throw
                    an error when attempting to delete a not existent file
                    key. Ignore this exception, any storage error of concern
                    will be triggered by the ``storage.save`` call below.
                    """
                    logger.debug(
                        'cache.storage.delete exception: %s', exception
                    )

                self.cache.storage.save(
                    name=self.get_full_filename(filename=filename),
                    content=ContentFile(content=b'')
                )

                partition_file = None

                try:
                    partition_file = self.files.create(filename=filename)
                    yield partition_file._open_for_writing(_acquire_lock=False)
                except Exception as exception:
                    logger.error(
                        'Unexpected exception while trying to save new '
                        'cache file; %s', exception, exc_info=True
                    )
                    if partition_file:
                        partition_file.delete(_acquire_lock=False)
                    else:
                        # If the CachePartitionFile entry was not created
                        # do manual clean up of the empty storage file
                        # created with the previous`self.cache.storage.save`.
                        self.cache.storage.delete(
                            name=self.get_full_filename(filename=filename)
                        )
                    raise
                else:
                    partition_file.close(_acquire_lock=False)
                    partition_file._update_size(_acquire_lock=False)
            finally:
                lock.release()
        except LockError:
            logger.debug('unable to obtain lock: %s', lock_name)
            raise

    def get_file(self, filename):
        return self.files.get(filename=filename)

    def get_file_lock_name(self, filename):
        return 'cache_partition-file-{}-{}-{}'.format(
            self.cache.pk, self.pk, filename
        )

    def get_full_filename(self, filename):
        CachePartition = apps.get_model(
            app_label='file_caching', model_name='CachePartition'
        )

        return CachePartition.get_combined_filename(
            parent=self.name, filename=filename
        )

    def get_total_size(self):
        """
        Return the actual usage of the cache partition.
        """
        return self.files.aggregate(
            file_size__sum=Sum('file_size')
        )['file_size__sum'] or 0

    def get_total_size_display(self):
        return filesizeformat(
            bytes_=self.get_total_size()
        )

    get_total_size_display.short_description = _('Current size')
    get_total_size_display.help_text = _(
        'Current size of the cache partition.'
    )

    @method_event(
        event=event_cache_partition_purged,
        event_manager_class=EventManagerMethodAfter,
        target='self'
    )
    def purge(self, user):
        self._event_actor = user
        for parition_file in self.files.all():
            try:
                parition_file.delete()
            except Exception as exception:
                logger.error(
                    'Unable to delete partition file ID: %d; %s',
                    parition_file.pk, exception
                )
                # Don't raise exceptions to allow the loop to continue and
                # avoid a single exception from stoping the purge.


class CachePartitionFileBusinessLogicMixin:
    def _lock_manager_get_lock_name(self, *args, **kwargs):
        return self.partition.get_file_lock_name(filename=self.filename)

    @acquire_lock_class_method
    def _open_for_writing(self):
        """
        Open the file for writing only. If the file is written to, the
        .update_size() must be called.
        """
        try:
            self._storage_object = self.partition.cache.storage.open(
                mode='wb', name=self.full_filename
            )
            return self._storage_object
        except Exception as exception:
            logger.error(
                'Unexpected exception opening the cache file; %s', exception,
                exc_info=True
            )
            raise

    @locked_class_method
    def _update_size(self):
        """
        Called after creation and initial write only.
        """
        self.file_size = self.partition.cache.storage.size(
            name=self.full_filename
        )
        self.save(
            update_fields=('file_size',)
        )
        if self.file_size > self.partition.cache.maximum_size:
            raise FileCachingException(
                'Cache partition file %s is bigger than the maximum cache '
                'size.'
            )

    @release_lock_class_method
    def close(self):
        if self._storage_object is not None:
            self._storage_object.close()
        self._storage_object = None

    @cached_property
    def full_filename(self):
        CachePartition = apps.get_model(
            app_label='file_caching', model_name='CachePartition'
        )

        return CachePartition.get_combined_filename(
            parent=self.partition.name, filename=self.filename
        )

    @contextmanager
    def open(self):
        """
        Open the file for reading only.
        """
        CachePartitionFile = apps.get_model(
            app_label='file_caching', model_name='CachePartitionFile'
        )

        lock_name = self._lock_manager_get_lock_name()
        try:
            logger.debug('trying to acquire lock: %s', lock_name)
            self._lock = LockingBackend.get_backend().acquire_lock(
                name=lock_name
            )
            CachePartitionFile.objects.filter(pk=self.pk).update(
                hits=F('hits') + 1
            )
            logger.debug('acquired lock: %s', lock_name)
            self._storage_object = None
            try:
                self._storage_object = self.partition.cache.storage.open(
                    mode='rb', name=self.full_filename
                )
            except Exception as exception:
                logger.error(
                    msg='Unexpected exception opening the cache file; %s',
                    args=(exception,), exc_info=True
                )
                raise
            else:
                yield self._storage_object
            finally:
                self.close(_acquire_lock=False)
                self._lock.release()
        except LockError:
            logger.debug('unable to obtain lock: %s', lock_name)
            raise
