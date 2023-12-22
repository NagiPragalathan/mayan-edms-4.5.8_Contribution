from django import forms
from django.utils.translation import ugettext_lazy as _

from mayan.apps.backends.forms import FormDynamicModelBackend

from .classes import CredentialBackend
from .models import StoredCredential


class StoredCredentialBackendSelectionForm(forms.Form):
    backend = forms.ChoiceField(
        choices=(), help_text=_('The backend to use for the credential.'),
        label=_('Backend')
    )

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['backend'].choices = CredentialBackend.get_choices()


class StoredCredentialBackendDynamicForm(FormDynamicModelBackend):
    class Meta:
        fields = ('label', 'internal_name', 'backend_data')
        model = StoredCredential
