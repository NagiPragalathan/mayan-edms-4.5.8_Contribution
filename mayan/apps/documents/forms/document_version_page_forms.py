from django import forms
from django.forms.formsets import formset_factory
from django.utils.translation import ugettext_lazy as _

from ..fields import DocumentVersionPageField, ThumbnailFormField

from .document_version_page_form_mixins import FormSetExtraFormKwargsMixin


class DocumentVersionPageForm(forms.Form):
    document_version_page = DocumentVersionPageField()

    def __init__(self, *args, **kwargs):
        instance = kwargs.pop('instance', None)
        transformation_instance_list = kwargs.pop(
            'transformation_instance_list', ()
        )
        super().__init__(*args, **kwargs)
        self.fields['document_version_page'].initial = instance
        self.fields['document_version_page'].widget.attrs.update(
            {
                'transformation_instance_list': transformation_instance_list
            }
        )


class DocumentVersionPageMappingForm(forms.Form):
    source_content_type = forms.IntegerField(
        label=_('Content type'), widget=forms.HiddenInput
    )
    source_object_id = forms.IntegerField(
        label=_('Object ID'), widget=forms.HiddenInput
    )
    source_label = forms.CharField(
        label=_('Source'), required=False,
        widget=forms.TextInput(
            attrs={'readonly': 'readonly'}
        )
    )
    source_thumbnail = ThumbnailFormField(required=False)
    target_page_number = forms.ChoiceField(
        choices=(), label=_('Destination page number'), required=False,
        widget=forms.widgets.Select(
            attrs={'size': 1, 'class': 'select2'}
        )
    )

    def __init__(self, *args, **kwargs):
        target_page_number_choices = kwargs.pop(
            'target_page_number_choices', ()
        )
        super().__init__(*args, **kwargs)
        self.fields['target_page_number'].choices = target_page_number_choices


class DocumentVersionPageMappingFormSet(
    FormSetExtraFormKwargsMixin, formset_factory(
        form=DocumentVersionPageMappingForm, extra=0
    )
):
    """
    Combined formset
    """
    def clean(self):
        set_of_target_page_numbers = set()
        for form in self.forms:
            cleaned_data_entry = form.cleaned_data
            target_page_number = cleaned_data_entry['target_page_number']
            if target_page_number != '0':
                if target_page_number in set_of_target_page_numbers:
                    form.add_error(
                        error=_('Target page number can\'t be repeated.'),
                        field='target_page_number'
                    )
                else:
                    set_of_target_page_numbers.add(target_page_number)
