import logging

from django.db import models, transaction
from django.urls import reverse
from django.utils.translation import ugettext_lazy as _

from mayan.apps.databases.model_mixins import ExtraDataModelMixin
from mayan.apps.common.signals import signal_mayan_pre_save
from mayan.apps.events.decorators import method_event
from mayan.apps.events.event_managers import EventManagerMethodAfter
from mayan.apps.storage.classes import DefinedStorageLazy

from ..events import event_document_file_deleted, event_document_file_edited
from ..literals import STORAGE_NAME_DOCUMENT_FILES
from ..managers import DocumentFileManager, ValidDocumentFileManager

from .document_file_model_mixins import DocumentFileBusinessLogicMixin
from .document_models import Document
from .model_mixins import HooksModelMixin

__all__ = ('DocumentFile', 'DocumentFileSearchResult')
logger = logging.getLogger(name=__name__)


def upload_to(instance, filename):
    return instance.document.document_type.get_upload_filename(
        instance=instance, filename=filename
    )


class DocumentFile(
    DocumentFileBusinessLogicMixin, ExtraDataModelMixin, HooksModelMixin,
    models.Model
):
    """
    Model that describes a document file and its properties
    Fields:
    * mimetype - File mimetype. MIME types are a standard way to describe the
    format of a file, in this case the file format of the document.
    Some examples: "text/plain" or "image/jpeg". Mayan uses this to determine
    how to render a document's file. More information:
    http://www.freeformatter.com/mime-types-list.html
    * encoding - File Encoding. The filesystem encoding of the document's
    file: binary 7-bit, binary 8-bit, text, base64, etc.
    * checksum - A hash/checkdigit/fingerprint generated from the document's
    binary data. Only identical documents will have the same checksum. If a
    document is modified after upload it's checksum will not match, used for
    detecting file tampering among other things.
    """
    _hooks_pre_create = []
    _pre_open_hooks = []
    _pre_save_hooks = []
    _post_save_hooks = []

    document = models.ForeignKey(
        on_delete=models.CASCADE, related_name='files', to=Document,
        verbose_name=_('Document')
    )
    timestamp = models.DateTimeField(
        auto_now_add=True, db_index=True, help_text=_(
            'The server date and time when the document file was processed.'
        ), verbose_name=_('Timestamp')
    )
    comment = models.TextField(
        blank=True, default='', help_text=_(
            'An optional short text describing the document file.'
        ), verbose_name=_('Comment')
    )
    # File related fields.
    file = models.FileField(
        storage=DefinedStorageLazy(name=STORAGE_NAME_DOCUMENT_FILES),
        upload_to=upload_to, verbose_name=_('File')
    )
    filename = models.CharField(
        blank=True, max_length=255, verbose_name=_('Filename')
    )
    mimetype = models.CharField(
        blank=True, editable=False, help_text=_(
            'The document file\'s file mimetype. MIME types are a '
            'standard way to describe the format of a file, in this case '
            'the file format of the document. Some examples: "text/plain" '
            'or "image/jpeg". '
        ), max_length=255, null=True, verbose_name=_('MIME type')
    )
    encoding = models.CharField(
        blank=True, editable=False, help_text=_(
            'The document file file encoding. binary 7-bit, binary 8-bit, '
            'text, base64, etc.'
        ), max_length=64, null=True, verbose_name=_('Encoding')
    )
    checksum = models.CharField(
        blank=True, db_index=True, editable=False, help_text=(
            'A hash/checkdigit/fingerprint generated from the document\'s '
            'binary data. Only identical documents will have the same '
            'checksum.'
        ), max_length=64, null=True, verbose_name=_('Checksum')
    )
    size = models.PositiveBigIntegerField(
        blank=True, db_index=True, editable=False, help_text=(
            'The size of the file in bytes.'
        ), null=True, verbose_name=_('Size')
    )

    class Meta:
        ordering = ('timestamp',)
        verbose_name = _('Document file')
        verbose_name_plural = _('Document files')

    objects = DocumentFileManager()
    valid = ValidDocumentFileManager()

    def __str__(self):
        return self.get_label()

    @method_event(
        action_object='document',
        event_manager_class=EventManagerMethodAfter,
        event=event_document_file_edited,
        target='self'
    )
    def _save(self, *args, **kwargs):
        user = getattr(self, '_event_actor', None)

        try:
            self.execute_pre_save_hooks()

            signal_mayan_pre_save.send(
                instance=self, sender=DocumentFile, user=user
            )

            result = super().save(*args, **kwargs)

            DocumentFile._execute_hooks(
                hook_list=DocumentFile._post_save_hooks,
                instance=self
            )
        except Exception as exception:
            logger.error(
                'Error saving document file for document "%s"; %s',
                self.document, exception, exc_info=True
            )
            raise
        else:
            return result

    @method_event(
        event_manager_class=EventManagerMethodAfter,
        event=event_document_file_deleted,
        target='document'
    )
    def delete(self, user=None, *args, **kwargs):
        if user:
            self._event_actor = user

        for page in self.pages.all():
            page._event_actor = getattr(self, '_event_actor', None)
            page.delete()

        name = self.file.name
        self.file.close()
        self.file.storage.delete(name=name)
        self.cache_partition.delete()

        with transaction.atomic():
            result = super().delete(*args, **kwargs)

            self.document.file_latest = self.get_document_file_latest()

            if self.document.files.exclude(pk=self.pk).count() == 0:
                self.document.is_stub = False

            self.document._event_ignore = True
            self.document.save(
                update_fields=('file_latest', 'is_stub')
            )

            return result

    def get_absolute_url(self):
        return reverse(
            viewname='documents:document_file_preview', kwargs={
                'document_file_id': self.pk
            }
        )

    def natural_key(self):
        return (
            self.checksum, self.document.natural_key()
        )
    natural_key.dependencies = ['documents.Document']

    def save(self, skip_introspection=False, *args, **kwargs):
        """
        Overloaded save method that updates the document file's checksum,
        mimetype, and page count when created.
        """
        self._event_keep_attributes = ('_event_actor',)
        new_document_file = not self.pk

        if new_document_file:
            result = self._create(*args, **kwargs)
            if not skip_introspection:
                self._introspect()
            return result
        else:
            return self._save(*args, **kwargs)


class DocumentFileSearchResult(DocumentFile):
    class Meta:
        proxy = True
