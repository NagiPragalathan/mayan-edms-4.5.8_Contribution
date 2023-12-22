import logging

from django.utils.translation import ugettext_lazy as _

from mayan.apps.django_gpg.models import Key
from mayan.apps.django_gpg.permissions import permission_key_sign
from mayan.apps.document_states.classes import WorkflowAction
from mayan.apps.document_states.exceptions import WorkflowStateActionError

from .models import DetachedSignature, EmbeddedSignature

logger = logging.getLogger(name=__name__)


class DocumentSignatureDetachedAction(WorkflowAction):
    form_field_widgets = {
        'key': {
            'class': 'django.forms.widgets.Select', 'kwargs': {
                'attrs': {'class': 'select2'}
            }
        },
        'passphrase': {
            'class': 'django.forms.widgets.PasswordInput',
        }
    }
    form_fields = {
        'passphrase': {
            'label': _('Passphrase'),
            'class': 'django.forms.CharField', 'kwargs': {
                'help_text': _(
                    'The passphrase to unlock the key and allow it to be '
                    'used to sign the document file.'
                ), 'required': False
            },
        },
    }
    label = _('Sign document (detached)')

    @classmethod
    def get_form_fields(cls):
        fields = super().get_form_fields()

        fields.update(
            {
                'key': {
                    'class': 'mayan.apps.views.fields.FormFieldFilteredModelChoice',
                    'help_text': _(
                        'Private key that will be used to sign the document '
                        'file.'
                    ),
                    'kwargs': {
                        'source_model': Key,
                        'permission': permission_key_sign
                    },
                    'label': _('Private key'),
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
                _('Key'), {
                    'fields': ('key', 'passphrase',)
                }
            ),
        )
        return fieldsets

    def get_arguments(self, context):
        latest_file = context['workflow_instance'].document.file_latest
        if not latest_file:
            raise WorkflowStateActionError(
                _(
                    'Document has no file to sign. You might be trying to '
                    'use this action in an initial state before the created '
                    'document is yet to be processed.'
                )
            )

        return {
            'document_file': latest_file,
            'key': Key.objects.get(
                pk=self.kwargs['key']
            ),
            'passphrase': self.kwargs.get('passphrase')
        }

    def execute(self, context):
        DetachedSignature.objects.sign_document_file(
            **self.get_arguments(context=context)
        )


class DocumentSignatureEmbeddedAction(DocumentSignatureDetachedAction):
    label = _('Sign document (embedded)')

    def execute(self, context):
        EmbeddedSignature.objects.sign_document_file(
            **self.get_arguments(context=context)
        )
