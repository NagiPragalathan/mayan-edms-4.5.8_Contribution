from django.db import models
from django.utils.translation import ugettext_lazy as _

from mayan.apps.acls.models import AccessControlList
from mayan.apps.databases.model_mixins import ExtraDataModelMixin
from mayan.apps.documents.permissions import permission_document_view
from mayan.apps.events.decorators import method_event
from mayan.apps.events.event_managers import (
    EventManagerMethodAfter, EventManagerSave
)

from ..events import event_workflow_template_edited

from .workflow_models import Workflow
from .workflow_state_model_mixins import WorkflowStateBusinessLogicMixin

__all__ = ('WorkflowState', 'WorkflowStateRuntimeProxy')


class WorkflowState(
    ExtraDataModelMixin, WorkflowStateBusinessLogicMixin, models.Model
):
    """
    Fields:
    * completion - Completion Amount - A user defined numerical value to help
    determine if the workflow of the document is nearing completion (100%).
    The Completion Amount will be determined by the completion value of the
    Actual State. Example: If the workflow has 3 states: registered, approved,
    archived; the admin could give the follow completion values to the
    states: 33%, 66%, 100%. If the Actual State of the document if approved,
    the Completion Amount will show 66%.
    """
    workflow = models.ForeignKey(
        on_delete=models.CASCADE, related_name='states', to=Workflow,
        verbose_name=_('Workflow')
    )
    label = models.CharField(
        help_text=_('A short text to describe the workflow state.'),
        max_length=255, verbose_name=_('Label')
    )
    initial = models.BooleanField(
        default=False,
        help_text=_(
            'The state at which the workflow will start in. Only one state '
            'can be the initial state.'
        ), verbose_name=_('Initial')
    )
    completion = models.IntegerField(
        blank=True, default=0, help_text=_(
            'The percent of completion that this state represents in '
            'relation to the workflow. Use numbers without the percent sign.'
        ), verbose_name=_('Completion')
    )

    class Meta:
        ordering = ('label',)
        unique_together = ('workflow', 'label')
        verbose_name = _('Workflow state')
        verbose_name_plural = _('Workflow states')

    def __str__(self):
        return self.label

    @method_event(
        action_object='self',
        event_manager_class=EventManagerMethodAfter,
        event=event_workflow_template_edited,
        target='workflow'
    )
    def delete(self, *args, **kwargs):
        return super().delete(*args, **kwargs)

    @method_event(
        event_manager_class=EventManagerSave,
        created={
            'action_object': 'self',
            'event': event_workflow_template_edited,
            'target': 'workflow'
        },
        edited={
            'action_object': 'self',
            'event': event_workflow_template_edited,
            'target': 'workflow'
        }
    )
    def save(self, *args, **kwargs):
        # Solve issue #557 "Break workflows with invalid input"
        # without using a migration.
        # Remove blank=True, remove this, and create a migration in the next
        # minor version.

        try:
            self.completion = int(self.completion)
        except (TypeError, ValueError):
            self.completion = 0

        if self.initial:
            self.workflow.states.all().update(initial=False)
        return super().save(*args, **kwargs)


class WorkflowStateRuntimeProxy(WorkflowState):
    class Meta:
        proxy = True
        verbose_name = _('Workflow state runtime proxy')
        verbose_name_plural = _('Workflow state runtime proxies')

    def get_documents(self, permission=None, user=None):
        """
        Provide a queryset of the documents. The queryset is optionally
        filtered by access.
        """
        queryset = super().get_documents()

        if permission and user:
            queryset = AccessControlList.objects.restrict_queryset(
                permission=permission, queryset=queryset,
                user=user
            )

        return queryset

    def get_document_count(self, user):
        """
        Return the numeric count of documents at this workflow state.
        The count is filtered by access.
        """
        return self.get_documents(
            permission=permission_document_view, user=user
        ).count()
