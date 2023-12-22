from django.db import models
from django.utils.translation import ugettext_lazy as _

from mayan.apps.databases.model_mixins import ExtraDataModelMixin
from mayan.apps.documents.models.document_type_models import DocumentType
from mayan.apps.events.decorators import method_event
from mayan.apps.events.event_managers import (
    EventManagerMethodAfter, EventManagerSave
)

from .events import event_smart_link_created, event_smart_link_edited
from .literals import INCLUSION_AND, INCLUSION_CHOICES, OPERATOR_CHOICES
from .managers import SmartLinkManager
from .model_mixins import (
    ResolvedSmartLinkBusinessLogicMixin, SmartLinkBusinessLogicMixin,
    SmartLinkConditionBusinessLogicMixin
)


class SmartLink(
    ExtraDataModelMixin, SmartLinkBusinessLogicMixin, models.Model
):
    """
    This model stores the basic fields for a smart link. Smart links allow
    linking documents using a programmatic method of conditions that mirror
    Django's database filter operations.
    """
    label = models.CharField(
        db_index=True, help_text=_('A short text describing the smart link.'),
        max_length=128, verbose_name=_('Label')
    )
    dynamic_label = models.CharField(
        blank=True, max_length=96, help_text=_(
            'Use this field to show a unique label depending on the '
            'document from which the smart link is being accessed.'
        ), verbose_name=_('Dynamic label')
    )
    enabled = models.BooleanField(default=True, verbose_name=_('Enabled'))
    document_types = models.ManyToManyField(
        related_name='smart_links', to=DocumentType,
        verbose_name=_('Document types')
    )

    objects = SmartLinkManager()

    class Meta:
        ordering = ('label',)
        verbose_name = _('Smart link')
        verbose_name_plural = _('Smart links')

    def __str__(self):
        return self.label

    @method_event(
        event_manager_class=EventManagerSave,
        created={
            'event': event_smart_link_created,
            'target': 'self'
        },
        edited={
            'event': event_smart_link_edited,
            'target': 'self'
        }
    )
    def save(self, *args, **kwargs):
        return super().save(*args, **kwargs)


class ResolvedSmartLink(ResolvedSmartLinkBusinessLogicMixin, SmartLink):
    """
    Proxy model to represent an already resolved smart link. Used for easier
    columns registration.
    """
    class Meta:
        proxy = True


class SmartLinkCondition(
    ExtraDataModelMixin, SmartLinkConditionBusinessLogicMixin, models.Model
):
    """
    This model stores a single smart link condition. A smart link is a
    collection of one of more smart link conditions.
    """
    smart_link = models.ForeignKey(
        on_delete=models.CASCADE, related_name='conditions', to=SmartLink,
        verbose_name=_('Smart link')
    )
    inclusion = models.CharField(
        choices=INCLUSION_CHOICES, default=INCLUSION_AND,
        help_text=_('The inclusion is ignored for the first item.'),
        max_length=16
    )
    foreign_document_data = models.CharField(
        help_text=_('This represents the metadata of all other documents.'),
        max_length=128, verbose_name=_('Foreign document attribute')
    )
    operator = models.CharField(choices=OPERATOR_CHOICES, max_length=16)
    expression = models.TextField(
        help_text=_(
            'The expression using document properties to be evaluated '
            'against the foreign document field.'
        ), verbose_name=_('Expression')
    )
    negated = models.BooleanField(
        default=False, help_text=_('Inverts the logic of the operator.'),
        verbose_name=_('Negated')
    )
    enabled = models.BooleanField(
        default=True, verbose_name=_('Enabled')
    )

    class Meta:
        verbose_name = _('Link condition')
        verbose_name_plural = _('Link conditions')

    def __str__(self):
        return self.get_full_label()

    @method_event(
        event_manager_class=EventManagerMethodAfter,
        event=event_smart_link_edited,
        target='smart_link'
    )
    def delete(self, *args, **kwargs):
        return super().delete(*args, **kwargs)

    @method_event(
        event_manager_class=EventManagerSave,
        created={
            'action_object': 'self',
            'event': event_smart_link_edited,
            'target': 'smart_link'
        },
        edited={
            'action_object': 'self',
            'event': event_smart_link_edited,
            'target': 'smart_link'
        }
    )
    def save(self, *args, **kwargs):
        return super().save(*args, **kwargs)
