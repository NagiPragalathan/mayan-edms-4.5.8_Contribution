import logging

from django import forms
from django.utils.translation import ugettext_lazy as _

from mayan.apps.backends.forms import FormDynamicModelBackend
from mayan.apps.documents.classes import DocumentFileAction
from mayan.apps.documents.forms.document_forms import DocumentForm
from mayan.apps.documents.literals import DEFAULT_DOCUMENT_FILE_ACTION_NAME
from mayan.apps.views.widgets import DropzoneWidget

from .models import Source
from .source_backends.base import SourceBackend

logger = logging.getLogger(name=__name__)


class NewDocumentForm(DocumentForm):
    class Meta(DocumentForm.Meta):
        exclude = ('label', 'description')


class NewDocumentFileForm(forms.Form):
    comment = forms.CharField(
        help_text=_('An optional comment to explain the upload.'),
        label=_('Comment'), required=False,
        widget=forms.widgets.Textarea(
            attrs={'rows': 4}
        )
    )
    action_name = forms.ChoiceField(
        label=_('Action'), help_text=_(
            'The action to take in regards to the pages of the new file '
            'being uploaded.'
        )
    )

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['action_name'].choices = DocumentFileAction.get_choices()
        self.fields['action_name'].initial = DEFAULT_DOCUMENT_FILE_ACTION_NAME


class UploadBaseForm(forms.Form):
    def __init__(self, *args, **kwargs):
        self.source = kwargs.pop('source')

        super().__init__(*args, **kwargs)


class SourceBackendSelectionForm(forms.Form):
    backend = forms.ChoiceField(
        choices=(), help_text=_(
            'The backend used to create the new source.'
        ), label=_('Backend')
    )

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['backend'].choices = SourceBackend.get_choices()


class SourceBackendSetupDynamicForm(FormDynamicModelBackend):
    class Meta:
        fields = ('label', 'enabled', 'backend_data')
        model = Source


class WebFormUploadFormHTML5(UploadBaseForm):
    file = forms.FileField(
        label=_('File'), widget=forms.widgets.FileInput()
    )

    dropzone = forms.CharField(
        label='', required=False, widget=DropzoneWidget
    )
