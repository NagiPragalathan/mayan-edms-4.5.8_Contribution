import json

from django.utils.translation import ugettext_lazy as _

from rest_framework.reverse import reverse

from mayan.apps.rest_api import serializers
from mayan.apps.rest_api.relations import (
    FilteredPrimaryKeyRelatedField, MultiKwargHyperlinkedIdentityField
)
from mayan.apps.user_management.serializers import UserSerializer

from ..models import WorkflowInstance, WorkflowInstanceLogEntry
from ..permissions import permission_workflow_tools

from .workflow_template_serializers import WorkflowTemplateSerializer
from .workflow_template_state_serializers import WorkflowTemplateStateSerializer
from .workflow_template_transition_serializers import WorkflowTemplateTransitionSerializer


class WorkflowInstanceLaunchSerializer(serializers.Serializer):
    workflow_template_id = FilteredPrimaryKeyRelatedField(
        help_text=_(
            'Primary key of the workflow template to launch.'
        ), label=_('Workflow template ID'),
        source_permission=permission_workflow_tools
    )

    def get_workflow_template_id_queryset(self):
        return self.context['document_type'].workflows.exclude(
            id__in=self.context['document'].workflows.values('id')
        )


class WorkflowInstanceLogEntrySerializer(serializers.ModelSerializer):
    document_url = MultiKwargHyperlinkedIdentityField(
        label=_('Document URL'), view_kwargs=(
            {
                'lookup_field': 'workflow_instance.document.pk',
                'lookup_url_kwarg': 'document_id',
            },
        ), view_name='rest_api:document-detail'
    )
    transition = WorkflowTemplateTransitionSerializer(
        label=_('Transition'), read_only=True
    )
    transition_id = FilteredPrimaryKeyRelatedField(
        help_text=_(
            'Primary key of the transition to be added.'
        ), label=_('Transition ID'),
        source_queryset_method='get_workflow_instance_transition_queryset',
        write_only=True
    )
    url = MultiKwargHyperlinkedIdentityField(
        label=_('URL'), view_kwargs=(
            {
                'lookup_field': 'workflow_instance.document.pk',
                'lookup_url_kwarg': 'document_id'
            },
            {
                'lookup_field': 'workflow_instance.pk',
                'lookup_url_kwarg': 'workflow_instance_id'
            },
            {
                'lookup_field': 'pk',
                'lookup_url_kwarg': 'workflow_instance_log_entry_id'
            }
        ), view_name='rest_api:workflow-instance-log-entry-detail'
    )
    user = UserSerializer(
        label=_('User'), read_only=True
    )
    workflow_instance_url = MultiKwargHyperlinkedIdentityField(
        label=_('Workflow instance URL'), view_kwargs=(
            {
                'lookup_field': 'workflow_instance.document.pk',
                'lookup_url_kwarg': 'document_id'
            },
            {
                'lookup_field': 'workflow_instance.pk',
                'lookup_url_kwarg': 'workflow_instance_id'
            }
        ), view_name='rest_api:workflow-instance-detail'
    )
    workflow_template_url = MultiKwargHyperlinkedIdentityField(
        label=_('Workflow template URL'), view_kwargs=(
            {
                'lookup_field': 'workflow_instance.workflow.pk',
                'lookup_url_kwarg': 'workflow_template_id'
            },
        ), view_name='rest_api:workflow-template-detail'
    )

    class Meta:
        fields = (
            'comment', 'datetime', 'document_url', 'extra_data', 'id',
            'transition', 'transition_id', 'url', 'user',
            'workflow_instance_url', 'workflow_template_url'
        )
        model = WorkflowInstanceLogEntry
        read_only_fields = (
            'datetime', 'document_url', 'id', 'transition',
            'url', 'user', 'workflow_instance_url', 'workflow_template_url'
        )

    def create(self, validated_data):
        return self.context['workflow_instance'].do_transition(
            transition=validated_data['transition_id'],
            comment=validated_data.get('comment'),
            extra_data=json.loads(
                s=validated_data.get('extra_data', '{}')
            ), user=self.context['request'].user
        )

    def get_workflow_instance_transition_queryset(self):
        return self.context['workflow_instance'].get_transition_choices(
            user=self.context['request'].user
        )


class WorkflowInstanceSerializer(serializers.ModelSerializer):
    workflow_template = WorkflowTemplateSerializer(
        label=_('Workflow template'), read_only=True, source='workflow'
    )
    context = serializers.SerializerMethodField(
        label=_('Context')
    )
    current_state = WorkflowTemplateStateSerializer(
        label=_('Current state'), read_only=True, source='get_current_state'
    )
    document_url = serializers.SerializerMethodField(
        label=_('Document URL')
    )
    last_log_entry = WorkflowInstanceLogEntrySerializer(
        label=_('Last log entry'), read_only=True,
        source='get_last_log_entry'
    )
    log_entries_url = serializers.SerializerMethodField(
        label=_('Log entries URL'), help_text=_(
            'A link to the entire history of this workflow.'
        )
    )
    log_entry_transitions_url = serializers.SerializerMethodField(
        label=_('Log entry transitions URL'), read_only=True
    )
    # DEPRECATION: Remove in version 5.0.
    workflow_template_url = serializers.SerializerMethodField(
        label=_('Workflow template URL')
    )
    url = serializers.SerializerMethodField(
        label=_('URL'), help_text=_(
            'API URL pointing to a workflow in relation to the '
            'document to which it is attached. This URL is different than '
            'the canonical workflow URL.'
        )
    )

    class Meta:
        fields = (
            'context', 'current_state', 'document_url', 'id',
            'last_log_entry', 'log_entries_url',
            'log_entry_transitions_url', 'url', 'workflow_template',
            'workflow_template_url'
        )
        model = WorkflowInstance
        read_only_fields = fields

    def get_document_url(self, instance):
        return reverse(
            viewname='rest_api:document-detail', kwargs={
                'document_id': instance.document.pk
            }, request=self.context['request'], format=self.context['format']
        )

    def get_context(self, instance):
        return {'workflow_instance_context': instance.loads()}

    def get_log_entries_url(self, instance):
        return reverse(
            viewname='rest_api:workflow-instance-log-entry-list', kwargs={
                'document_id': instance.document.pk,
                'workflow_instance_id': instance.pk
            }, request=self.context['request'], format=self.context['format']
        )

    def get_log_entry_transitions_url(self, instance):
        return reverse(
            viewname='rest_api:workflow-instance-log-entry-transition-list',
            kwargs={
                'document_id': instance.document.pk,
                'workflow_instance_id': instance.pk
            }, request=self.context['request'], format=self.context['format']
        )

    def get_url(self, instance):
        return reverse(
            viewname='rest_api:workflow-instance-detail', kwargs={
                'document_id': instance.document.pk,
                'workflow_instance_id': instance.pk
            }, request=self.context['request'], format=self.context['format']
        )

    def get_workflow_template_url(self, instance):
        return reverse(
            viewname='rest_api:workflow-template-detail', kwargs={
                'workflow_template_id': instance.workflow.pk
            }, request=self.context['request'], format=self.context['format']
        )
