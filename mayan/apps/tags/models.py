from django.db import models
from django.urls import reverse
from django.utils.translation import ugettext_lazy as _

from mayan.apps.databases.model_mixins import ExtraDataModelMixin
from mayan.apps.documents.models.document_models import Document
from mayan.apps.events.decorators import method_event
from mayan.apps.events.event_managers import EventManagerSave

from .events import event_tag_created, event_tag_edited
from .model_mixins import TagBusinessLogicMixin


class Tag(ExtraDataModelMixin, TagBusinessLogicMixin, models.Model):
    """
    This model represents a binary property that can be applied to a document.
    The tag can have a label and a color.
    """
    label = models.CharField(
        db_index=True, help_text=_(
            'A short text used as the tag name.'
        ), max_length=128, unique=True, verbose_name=_('Label')
    )
    color = models.CharField(
        help_text=_('The RGB color values for the tag.'),
        max_length=7, verbose_name=_('Color')
    )
    documents = models.ManyToManyField(
        related_name='tags', to=Document, verbose_name=_('Documents')
    )

    class Meta:
        ordering = ('label',)
        verbose_name = _('Tag')
        verbose_name_plural = _('Tags')

    def __str__(self):
        return self.label

    def get_absolute_url(self):
        return reverse(
            viewname='tags:tag_document_list', kwargs={'tag_id': self.pk}
        )

    @method_event(
        event_manager_class=EventManagerSave,
        created={
            'event': event_tag_created,
            'target': 'self'
        },
        edited={
            'event': event_tag_edited,
            'target': 'self'
        }
    )
    def save(self, *args, **kwargs):
        return super().save(*args, **kwargs)


class DocumentTag(Tag):
    class Meta:
        proxy = True
        verbose_name = _('Document tag')
        verbose_name_plural = _('Document tags')
