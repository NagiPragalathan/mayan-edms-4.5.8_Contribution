import hashlib

from django.apps import apps
from django.core import serializers
from django.db.models import F, Max, Q
from django.utils.translation import ugettext_lazy as _

from mayan.apps.documents.models.document_models import Document

from ..literals import WORKFLOW_ACTION_ON_ENTRY, WORKFLOW_ACTION_ON_EXIT


class WorkflowStateBusinessLogicMixin:
    @property
    def entry_actions(self):
        return self.actions.filter(when=WORKFLOW_ACTION_ON_ENTRY)

    @property
    def exit_actions(self):
        return self.actions.filter(when=WORKFLOW_ACTION_ON_EXIT)

    def get_actions_display(self):
        field_list = [
            str(field) for field in self.actions.all()
        ]
        field_list.sort()

        return ', '.join(field_list)

    get_actions_display.short_description = _('Actions')

    def get_escalations_display(self):
        field_list = [
            str(field) for field in self.escalations.all()
        ]
        field_list.sort()

        return ', '.join(field_list)

    get_escalations_display.short_description = _('Escalations')

    def get_documents(self):
        WorkflowInstanceLogEntry = apps.get_model(
            app_label='document_states',
            model_name='WorkflowInstanceLogEntry'
        )

        latest_entries = WorkflowInstanceLogEntry.objects.annotate(
            max_datetime=Max(
                'workflow_instance__log_entries__datetime'
            )
        ).filter(
            datetime=F('max_datetime')
        )

        state_latest_entries = latest_entries.filter(
            transition__destination_state=self
        )

        return Document.valid.filter(
            Q(
                workflows__pk__in=state_latest_entries.values_list(
                    'workflow_instance', flat=True
                )
            ) | Q(
                workflows__log_entries__isnull=True,
                workflows__workflow__states=self,
                workflows__workflow__states__initial=True
            )
        ).distinct()

    def get_hash(self):
        result = hashlib.sha256(
            string=serializers.serialize(
                format='json', queryset=(self,)
            ).encode()
        )

        for action in self.actions.all():
            result.update(
                action.get_hash().encode()
            )

        for escalation in self.escalations.all():
            result.update(
                escalation.get_hash().encode()
            )

        return result.hexdigest()
