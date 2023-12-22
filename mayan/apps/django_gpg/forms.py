from django import forms
from django.utils.html import escape
from django.utils.translation import ugettext_lazy as _

from mayan.apps.views.forms import DetailForm

from .models import Key


class KeyDetailForm(DetailForm):
    def __init__(self, *args, **kwargs):
        instance = kwargs['instance']

        extra_fields = (
            {
                'field': 'key_id', 'label': _('Key ID')
            },
            {
                'func': lambda x: escape(instance.user_id),
                'label': _('User ID')
            },
            {
                'field': 'creation_date', 'label': _('Creation date'),
                'widget': forms.widgets.DateInput
            },
            {
                'func': lambda x: instance.expiration_date or _('None'),
                'label': _('Expiration date'),
                'widget': forms.widgets.DateInput
            },
            {
                'field': 'fingerprint', 'label': _('Fingerprint')
            },
            {
                'field': 'length', 'label': _('Length')
            },
            {
                'field': 'algorithm', 'label': _('Algorithm')
            },
            {
                'func': lambda x: instance.get_key_type_display(),
                'label': _('Type')
            }
        )

        kwargs['extra_fields'] = extra_fields
        super().__init__(*args, **kwargs)

    class Meta:
        fields = ()
        model = Key


class KeySearchForm(forms.Form):
    term = forms.CharField(
        label=_('Term'),
        help_text=_('Name, e-mail, key ID or key fingerprint to look for.')
    )
