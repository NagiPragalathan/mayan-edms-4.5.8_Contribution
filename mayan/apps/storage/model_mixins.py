import logging

from django.core.files.base import ContentFile
from django.db import models
from django.template.defaultfilters import filesizeformat
from django.utils.translation import ugettext_lazy as _, ugettext

from mayan.apps.events.decorators import method_event
from mayan.apps.events.event_managers import EventManagerMethodAfter

from .events import event_download_file_downloaded

logger = logging.getLogger(name=__name__)


class DatabaseFileModelMixin(models.Model):
    filename = models.CharField(
        db_index=True, max_length=255, verbose_name=_('Filename')
    )
    datetime = models.DateTimeField(
        auto_now_add=True, verbose_name=_('Date time')
    )

    class Meta:
        abstract = True

    def delete(self, *args, **kwargs):
        name = self.file.name
        self.file.close()

        if name:
            self.file.storage.delete(name=name)
        return super().delete(*args, **kwargs)

    def open(self, **kwargs):
        # Some storage class file do not provide a mode attribute.
        # In that case default to read only in binary mode.
        # Python's default is read only in text format which does not work
        # for this use case.
        # https://docs.python.org/3/library/functions.html#open
        mode = getattr(self.file.file, 'mode', 'rb')

        open_kwargs = {
            'mode': mode,
            'name': self.file.name
        }

        # Close the self.file object as Django generates a new descriptor
        # when the file field is accessed.
        # From django/db/models/fields/files.py.
        """
        The descriptor for the file attribute on the model instance. Return a
        FieldFile when accessed so you can write code like::

            >>> from myapp.models import MyModel
            >>> instance = MyModel.objects.get(pk=1)
            >>> instance.file.size

        Assign a file object on assignment so you can do::

            >>> with open('/path/to/hello.world', 'r') as f:
            ...     instance.file = File(f)
        """
        self.file.close()
        self.file.file.close()

        # Ensure the caller cannot specify an alternate filename.
        name = kwargs.pop('name', None)

        if name:
            logger.warning(
                'Caller tried to specify an alternate filename: %s', name
            )

        open_kwargs.update(**kwargs)

        return self.file.storage.open(**open_kwargs)

    def save(self, *args, **kwargs):
        if not self.file:
            self.file = ContentFile(
                content=b'', name=self.filename or ugettext('Unnamed file')
            )

        self.filename = self.filename or str(self.file)
        super().save(*args, **kwargs)


class DownloadFileBusinessLogicMixin:
    @method_event(
        event_manager_class=EventManagerMethodAfter,
        event=event_download_file_downloaded,
        target='self'
    )
    def get_download_file_object(self):
        return self.open(mode='rb')

    def get_size_display(self):
        return filesizeformat(bytes_=self.file.size)

    get_size_display.short_description = _('Size')

    def get_user_display(self):
        if self.user.get_full_name():
            return self.user.get_full_name()
        else:
            return self.user.username
    get_user_display.short_description = _('User')
