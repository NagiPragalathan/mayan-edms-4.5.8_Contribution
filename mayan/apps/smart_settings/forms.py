import yaml

from django import forms
from django.core.exceptions import ValidationError
from django.utils.translation import ugettext_lazy as _

from mayan.apps.common.serialization import yaml_load


class SettingForm(forms.Form):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.setting = self.initial['setting']

        if self.setting.choices:
            self.fields['value'] = forms.ChoiceField(
                choices=list(
                    zip(self.setting.choices, self.setting.choices)
                ), required=True
            )
        else:
            self.fields['value'] = forms.CharField(
                required=False, widget=forms.widgets.Textarea()
            )

        self.fields['value'].label = _('Value')
        self.fields['value'].help_text = self.setting.help_text or _(
            'Enter the new setting value.'
        )
        self.fields['value'].initial = self.setting.serialized_value

    def clean(self):
        try:
            yaml_load(
                stream=self.cleaned_data['value']
            )
        except yaml.YAMLError:
            raise ValidationError(
                message=_(
                    '"%s" not a valid entry.'
                ) % self.cleaned_data['value']
            )
        else:
            self.setting.validate(
                raw_value=self.cleaned_data['value']
            )
