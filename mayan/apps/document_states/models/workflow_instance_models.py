from django.conf import settings
from django.core.exceptions import ValidationError
from django.db import models
from django.urls import reverse
from django.utils.translation import ugettext_lazy as _

from mayan.apps.databases.model_mixins import ExtraDataModelMixin
from mayan.apps.documents.models.document_models import Document
from mayan.apps.events.decorators import method_event
from mayan.apps.events.event_managers import EventManagerSave

from ..events import (
    event_workflow_instance_created, event_workflow_instance_transitioned
)
from ..managers import ValidWorkflowInstanceManager

from .workflow_instance_model_mixins import (
    WorkflowInstanceBusinessLogicMixin,
    WorkflowInstanceLogEntryBusinessLogicMixin
)
from .workflow_models import Workflow

__all__ = ('WorkflowInstance', 'WorkflowInstanceLogEntry')


class WorkflowInstance(
    ExtraDataModelMixin, WorkflowInstanceBusinessLogicMixin, models.Model
):
    workflow = models.ForeignKey(
        on_delete=models.CASCADE, related_name='instances', to=Workflow,
        verbose_name=_('Workflow')
    )
    datetime = models.DateTimeField(
        auto_now_add=True, db_index=True, help_text=_(
            'Workflow instance creation date time.'
        ), verbose_name=_('Datetime')
    )
    document = models.ForeignKey(
        on_delete=models.CASCADE, related_name='workflows', to=Document,
        verbose_name=_('Document')
    )
    context = models.TextField(
        blank=True, verbose_name=_('Context')
    )

    objects = models.Manager()
    valid = ValidWorkflowInstanceManager()

    class Meta:
        ordering = ('workflow',)
        unique_together = ('document', 'workflow')
        verbose_name = _('Workflow instance')
        verbose_name_plural = _('Workflow instances')

    def __str__(self):
        return str(self.workflow)

    def get_absolute_url(self):
        return reverse(
            viewname='document_states:workflow_instance_detail', kwargs={
                'workflow_instance_id': self.pk
            }
        )

    @method_event(
        event_manager_class=EventManagerSave,
        created={
            'action_object': 'document',
            'event': event_workflow_instance_created,
            'target': 'self'
        }
    )
    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)


class WorkflowInstanceLogEntry(
    WorkflowInstanceLogEntryBusinessLogicMixin, models.Model
):
    """
    Fields:
    * user - The user who last transitioned the document from a state to the
    Actual State.
    * datetime - Date Time - The date and time when the last user transitioned
    the document state to the Actual state.
    """
    workflow_instance = models.ForeignKey(
        on_delete=models.CASCADE, related_name='log_entries',
        to=WorkflowInstance, verbose_name=_('Workflow instance')
    )
    datetime = models.DateTimeField(
        auto_now_add=True, db_index=True, verbose_name=_('Datetime')
    )
    transition = models.ForeignKey(
        on_delete=models.CASCADE, to='WorkflowTransition',
        verbose_name=_('Transition')
    )
    user = models.ForeignKey(
        blank=True, null=True, on_delete=models.CASCADE,
        to=settings.AUTH_USER_MODEL, verbose_name=_('User')
    )
    comment = models.TextField(
        blank=True, verbose_name=_('Comment')
    )
    extra_data = models.TextField(
        blank=True, verbose_name=_('Extra data')
    )

    class Meta:
        ordering = ('datetime',)
        verbose_name = _('Workflow instance log entry')
        verbose_name_plural = _('Workflow instance log entries')

    def __str__(self):
        return str(self.transition)

    def clean(self):
        if self.transition not in self.workflow_instance.get_transition_choices(user=self.user):
            raise ValidationError(
                message=_('Not a valid transition choice.')
            )

    @method_event(
        event_manager_class=EventManagerSave,
        created={
            'action_object': 'workflow_instance.document',
            'event': event_workflow_instance_transitioned,
            'target': 'workflow_instance'
        }
    )
    def save(self, *args, **kwargs):
        result = super().save(*args, **kwargs)
        context = self.workflow_instance.get_context()
        context.update(
            {
                'entry_log': self
            }
        )

        for action in self.transition.origin_state.exit_actions.filter(enabled=True):
            context.update(
                {
                    'action': action,
                }
            )
            action.execute(
                context=context, workflow_instance=self.workflow_instance
            )

        for action in self.transition.destination_state.entry_actions.filter(enabled=True):
            context.update(
                {
                    'action': action,
                }
            )
            action.execute(
                context=context, workflow_instance=self.workflow_instance
            )

        return result
