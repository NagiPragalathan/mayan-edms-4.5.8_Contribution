from django.db import models
from django.urls import reverse
from django.utils.translation import ugettext_lazy as _

from mayan.apps.acls.models import AccessControlList
from mayan.apps.common.validators import validate_internal_name
from mayan.apps.databases.model_mixins import ExtraDataModelMixin
from mayan.apps.documents.models.document_models import Document
from mayan.apps.documents.models.document_type_models import DocumentType
from mayan.apps.documents.permissions import permission_document_view
from mayan.apps.events.decorators import method_event
from mayan.apps.events.event_managers import EventManagerSave

from ..events import (
    event_workflow_template_created, event_workflow_template_edited
)
from ..managers import WorkflowManager

from .workflow_model_mixins import WorkflowBusinessLogicMixin

__all__ = ('Workflow', 'WorkflowRuntimeProxy')


class Workflow(
    ExtraDataModelMixin, WorkflowBusinessLogicMixin, models.Model
):
    """
    Fields:
    * label - Identifier. A name/label to call the workflow
    """
    auto_launch = models.BooleanField(
        default=True, help_text=_(
            'Launch workflow when document is created.'
        ), verbose_name=_('Auto launch')
    )
    internal_name = models.CharField(
        db_index=True, help_text=_(
            'This value will be used by other apps to reference this '
            'workflow. Can only contain letters, numbers, and underscores.'
        ), max_length=255, unique=True, validators=[validate_internal_name],
        verbose_name=_('Internal name')
    )
    label = models.CharField(
        help_text=_('A short text to describe the workflow.'),
        max_length=255, unique=True, verbose_name=_('Label')
    )
    document_types = models.ManyToManyField(
        related_name='workflows', to=DocumentType, verbose_name=_(
            'Document types'
        )
    )

    objects = WorkflowManager()

    class Meta:
        ordering = ('label',)
        verbose_name = _('Workflow')
        verbose_name_plural = _('Workflows')

    def __str__(self):
        return self.label

    def get_absolute_url(self):
        return reverse(viewname='document_states:workflow_template_list')

    def delete(self, *args, **kwargs):
        self.cache_partition.delete()
        return super().delete(*args, **kwargs)

    @method_event(
        event_manager_class=EventManagerSave,
        created={
            'event': event_workflow_template_created,
            'target': 'self'
        },
        edited={
            'event': event_workflow_template_edited,
            'target': 'self'
        }
    )
    def save(self, *args, **kwargs):
        return super().save(*args, **kwargs)


class WorkflowRuntimeProxy(Workflow):
    class Meta:
        proxy = True
        verbose_name = _('Workflow runtime proxy')
        verbose_name_plural = _('Workflow runtime proxies')

    def get_documents(self, permission=None, user=None):
        """
        Provide a queryset of the documents. The queryset is optionally
        filtered by access.
        """
        queryset = Document.valid.filter(workflows__workflow=self)

        if permission and user:
            queryset = AccessControlList.objects.restrict_queryset(
                permission=permission, queryset=queryset,
                user=user
            )

        return queryset

    def get_document_count(self, user):
        """
        Return the numeric count of documents executing this workflow.
        The count is filtered by access.
        """
        return self.get_documents(
            permission=permission_document_view, user=user
        ).count()
