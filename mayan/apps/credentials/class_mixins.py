from django.apps import apps
from django.utils.translation import ugettext_lazy as _

from .permissions import permission_credential_use


class BackendMixinCredentials:
    @classmethod
    def get_form_fields(cls):
        StoredCredential = apps.get_model(
            app_label='credentials', model_name='StoredCredential'
        )

        fields = super().get_form_fields()

        fields.update(
            {
                'stored_credential_id': {
                    'class': 'mayan.apps.views.fields.FormFieldFilteredModelChoice',
                    'help_text': _(
                        'The credential entry to use for authentication.'
                    ),
                    'kwargs': {
                        'source_model': StoredCredential,
                        'permission': permission_credential_use
                    },
                    'label': _('Credential'),
                    'required': True
                }
            }
        )

        return fields

    @classmethod
    def get_form_fieldsets(cls):
        fieldsets = super().get_form_fieldsets()

        fieldsets += (
            (
                _('Authentication'), {
                    'fields': (
                        'stored_credential_id',
                    )
                },
            ),
        )

        return fieldsets

    def get_credential(self):
        StoredCredential = apps.get_model(
            app_label='credentials', model_name='StoredCredential'
        )

        stored_credential_id = self.kwargs.get('stored_credential_id')

        if stored_credential_id:
            return StoredCredential.objects.get(
                pk=stored_credential_id
            ).get_backend_data()


class BackendMixinCredentialsOptional(BackendMixinCredentials):
    @classmethod
    def get_form_fields(cls):
        fields = super().get_form_fields()

        fields['stored_credential_id']['required'] = False
        fields['stored_credential_id']['help_text'] = _(
            'Optional credential entry to use for authentication.'
        )

        return fields
