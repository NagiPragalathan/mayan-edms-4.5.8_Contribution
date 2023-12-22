from django import forms
from django.utils.translation import ugettext_lazy as _

from mayan.apps.views.forms import Form

from .literals import MATCH_ALL_FIELD_CHOICES, MATCH_ALL_FIELD_NAME


class AdvancedSearchForm(Form):
    def __init__(self, *args, **kwargs):
        kwargs['data'] = kwargs['data'].copy()
        self.search_model = kwargs.pop('search_model')
        super().__init__(*args, **kwargs)

        fieldsets_dict = {}

        self.fields[MATCH_ALL_FIELD_NAME] = forms.ChoiceField(
            choices=MATCH_ALL_FIELD_CHOICES, widget=forms.RadioSelect,
            label=_('Match all'), help_text=_(
                'Return only results that match all fields.'
            ), required=False
        )

        for search_field in self.search_model.search_fields_label_sorted:
            if search_field.concrete and not search_field.field_name == 'id':
                self.fields[search_field.field_name] = forms.CharField(
                    help_text=search_field.get_help_text(),
                    label=search_field.label, required=False,
                    widget=forms.widgets.TextInput(
                        attrs={'type': 'search'}
                    )
                )

                # Build the fieldset dictionary.
                model = search_field.field_name_model_list[0]

                model_verbose_name_plural = model._meta.verbose_name_plural

                fieldsets_dict.setdefault(
                    model_verbose_name_plural, {
                        'fields': []
                    }
                )
                fieldsets_dict[model_verbose_name_plural]['fields'].append(
                    search_field.field_name
                )

        # Convert the fieldset dictionary to the standard fieldset tuple.
        fieldsets = ()

        fieldsets += (
            _('Search logic'), {
                'fields': (MATCH_ALL_FIELD_NAME,)
            }
        ),

        keys = list(
            fieldsets_dict.keys()
        )
        keys.sort()

        for key in keys:
            fieldsets += (
                key, fieldsets_dict[key]
            ),

        self.fieldsets = fieldsets


class SearchForm(Form):
    q = forms.CharField(
        max_length=128, label=_('Search terms'), required=False,
        widget=forms.widgets.TextInput(
            attrs={'type': 'search'}
        )
    )
