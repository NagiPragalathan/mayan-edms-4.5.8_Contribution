from django.utils.text import format_lazy
from django.utils.translation import ugettext_lazy as _

from mayan.apps.documents.models.document_models import Document
from mayan.apps.templating.fields import ModelTemplateField
from mayan.apps.views.forms import ModelForm

from .models import WebLink


class WebLinkForm(ModelForm):
    fieldsets = (
        (
            _('General'), {
                'fields': ('label', 'enabled')
            },
        ),
        (
            _('Templating'), {
                'fields': ('template',)
            },
        ),
    )

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['template'] = ModelTemplateField(
            initial_help_text=format_lazy(
                '{} ', self.fields['template'].help_text
            ), label=self.fields['template'].label, model=Document,
            model_variable='document', required=True
        )

    class Meta:
        fields = ('label', 'enabled', 'template')
        model = WebLink
