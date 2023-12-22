from django import forms
from django.forms.formsets import formset_factory
from django.utils.translation import ugettext_lazy as _


class DocumentDownloadForm(forms.Form):
    document_file_id = forms.CharField(
        label=_('Document file ID'), widget=forms.HiddenInput
    )
    document = forms.CharField(
        label=_('Document'), required=False,
        widget=forms.TextInput(
            attrs={
                'readonly': 'readonly'
            }
        )
    )
    document_file = forms.CharField(
        label=_('Document file'), required=False,
        widget=forms.TextInput(
            attrs={
                'readonly': 'readonly'
            }
        )
    )
    include = forms.BooleanField(
        initial=True, label=_('Include'), required=False
    )


DocumentDownloadFormSet = formset_factory(form=DocumentDownloadForm, extra=0)
