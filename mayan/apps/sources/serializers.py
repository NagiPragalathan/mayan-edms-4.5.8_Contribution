from django.utils.translation import ugettext_lazy as _

from rest_framework.reverse import reverse

from mayan.apps.permissions.serializers import PermissionSerializer
from mayan.apps.rest_api import serializers

from .models import Source


class SourceBackendActionInterfaceArgumentSerializer(serializers.Serializer):
    default = serializers.SerializerMethodField(
        label=_('Default')
    )
    has_default = serializers.BooleanField(
        label=_('Has default?')
    )
    help_text = serializers.CharField(
        label=_('Help text')
    )
    name = serializers.CharField(
        label=_('Name')
    )
    required = serializers.BooleanField(
        label=_('Required')
    )

    def get_default(self, instance):
        if instance.has_default:
            return instance.default
        else:
            return


class SourceBackendActionInterfaceSerializer(serializers.Serializer):
    arguments = SourceBackendActionInterfaceArgumentSerializer(
        label=_('Arguments'), many=True, read_only=True,
        source='arguments_visible'
    )
    name = serializers.CharField(
        label=_('Name')
    )


class SourceBackendActionSerializer(serializers.Serializer):
    accept_files = serializers.BooleanField(
        label=_('Accept files'), read_only=True
    )
    arguments = serializers.JSONField(
        help_text=_(
            'Optional arguments for the action. Must be JSON formatted.'
        ), initial={}, label=_('Arguments'), required=False,
        write_only=True
    )
    confirmation = serializers.BooleanField(
        label=_('Confirmation'), read_only=True
    )
    execute_url = serializers.SerializerMethodField(
        label=_('Execute URL'), read_only=True
    )
    interfaces = SourceBackendActionInterfaceSerializer(
        label=_('Interfaces'), many=True, read_only=True,
        source='interface_visible_list'
    )
    name = serializers.CharField(
        label=_('name'), read_only=True
    )
    permission = PermissionSerializer(
        label=_('Permission'), read_only=True
    )
    source_id = serializers.SerializerMethodField()
    source_url = serializers.SerializerMethodField()
    url = serializers.SerializerMethodField(
        label=_('URL'), read_only=True
    )

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        action = self.context.get('action')

        if action:
            if action.accept_files:
                self.fields['file'] = serializers.FileField(
                    help_text=_('Binary content for the new file.'),
                    use_url=False, write_only=True
                )

    def get_execute_url(self, instance):
        return reverse(
            viewname='rest_api:source_action-execute', kwargs={
                'source_id': instance.source.pk,
                'action_name': instance.name
            }, request=self.context['request'],
            format=self.context['format']
        )

    def get_source_id(self, instance):
        return instance.source.pk

    def get_source_url(self, instance):
        return reverse(
            viewname='rest_api:source-detail', kwargs={
                'source_id': instance.source.pk,
            }, request=self.context['request'],
            format=self.context['format']
        )

    def get_url(self, instance):
        return reverse(
            viewname='rest_api:source_action-detail', kwargs={
                'source_id': instance.source.pk,
                'action_name': instance.name
            }, request=self.context['request'],
            format=self.context['format']
        )


class SourceSerializer(serializers.HyperlinkedModelSerializer):
    actions_url = serializers.SerializerMethodField(
        label=_('Actions URL')
    )

    class Meta:
        extra_kwargs = {
            'url': {
                'lookup_field': 'pk', 'lookup_url_kwarg': 'source_id',
                'view_name': 'rest_api:source-detail'
            },
        }
        fields = (
            'actions_url', 'backend_data', 'backend_path', 'enabled', 'id',
            'label', 'url'
        )
        model = Source
        read_only_fields = ('actions', 'id', 'url')

    def get_actions_url(self, instance):
        return reverse(
            viewname='rest_api:source_action-list', kwargs={
                'source_id': instance.pk,
            }, request=self.context['request'],
            format=self.context['format']
        )
