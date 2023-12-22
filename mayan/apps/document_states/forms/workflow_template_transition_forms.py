from django import forms
from django.forms.formsets import formset_factory
from django.utils.translation import ugettext_lazy as _

from mayan.apps.templating.fields import ModelTemplateField

from ..models import WorkflowInstance, WorkflowTransition


class WorkflowTransitionForm(forms.ModelForm):
    def __init__(self, workflow, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.fields[
            'origin_state'
        ].queryset = self.fields[
            'origin_state'
        ].queryset.filter(workflow=workflow)

        self.fields[
            'destination_state'
        ].queryset = self.fields[
            'destination_state'
        ].queryset.filter(workflow=workflow)

        self.fields['condition'] = ModelTemplateField(
            initial_help_text=self.fields['condition'].help_text,
            label=self.fields['condition'].label, model=WorkflowInstance,
            model_variable='workflow_instance', required=False
        )

    class Meta:
        fields = ('label', 'origin_state', 'destination_state', 'condition')
        model = WorkflowTransition


class WorkflowTransitionTriggerEventRelationshipForm(forms.Form):
    namespace = forms.CharField(
        label=_('Namespace'), required=False,
        widget=forms.TextInput(
            attrs={'readonly': 'readonly'}
        )
    )
    label = forms.CharField(
        label=_('Label'), required=False,
        widget=forms.TextInput(
            attrs={'readonly': 'readonly'}
        )
    )
    relationship = forms.ChoiceField(
        choices=(
            ('no', _('No')),
            ('yes', _('Yes')),
        ), label=_('Enabled'), widget=forms.RadioSelect()
    )

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.fields['namespace'].initial = self.initial['event_type'].namespace
        self.fields['label'].initial = self.initial['event_type'].label

        relationship = self.initial['transition'].trigger_events.filter(
            event_type=self.initial['event_type']
        )

        if relationship.exists():
            self.fields['relationship'].initial = 'yes'
        else:
            self.fields['relationship'].initial = 'no'

    def save(self):
        relationship = self.initial['transition'].trigger_events.filter(
            event_type=self.initial['event_type']
        )

        if self.cleaned_data['relationship'] == 'no':
            relationship.delete()
        elif self.cleaned_data['relationship'] == 'yes':
            if not relationship.exists():
                self.initial['transition'].trigger_events.create(
                    event_type=self.initial['event_type']
                )


WorkflowTransitionTriggerEventRelationshipFormSet = formset_factory(
    form=WorkflowTransitionTriggerEventRelationshipForm, extra=0
)
