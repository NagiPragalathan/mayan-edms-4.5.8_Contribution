from django import forms
from django.utils.translation import ugettext_lazy as _

from mayan.apps.backends.forms import FormDynamicModelBackend
from mayan.apps.templating.fields import ModelTemplateField

from ..classes import WorkflowAction
from ..models import (
    WorkflowStateEscalation, WorkflowInstance, WorkflowState,
    WorkflowStateAction
)


class WorkflowTemplateStateActionDynamicForm(FormDynamicModelBackend):
    class Meta:
        fields = ('label', 'when', 'enabled', 'condition', 'backend_data')
        model = WorkflowStateAction
        widgets = {'backend_data': forms.widgets.HiddenInput}

    def __init__(self, request, user=None, *args, **kwargs):
        self.request = request
        self.user = user
        result = super().__init__(*args, **kwargs)

        self.fields['condition'] = ModelTemplateField(
            initial_help_text=self.fields['condition'].help_text,
            label=self.fields['condition'].label, model=WorkflowInstance,
            model_variable='workflow_instance', required=False
        )

        return result


class WorkflowTemplateStateActionSelectionForm(forms.Form):
    klass = forms.ChoiceField(
        choices=(), help_text=_('The action type for this action entry.'),
        label=_('Action'), widget=forms.Select(
            attrs={'class': 'select2'}
        )
    )

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.fields['klass'].choices = WorkflowAction.get_choices()


class WorkflowTemplateStateEscalationForm(forms.ModelForm):
    def __init__(self, workflow_template_state, *args, **kwargs):
        self.workflow_template_state = workflow_template_state
        super().__init__(*args, **kwargs)

        self.fields[
            'transition'
        ].queryset = self.workflow_template_state.workflow.transitions.filter(
            origin_state=self.workflow_template_state
        )

        self.fields['condition'] = ModelTemplateField(
            initial_help_text=self.fields['condition'].help_text,
            label=self.fields['condition'].label, model=WorkflowInstance,
            model_variable='workflow_instance', required=False
        )

    class Meta:
        fields = (
            'enabled', 'transition', 'priority', 'unit', 'amount',
            'condition'
        )
        model = WorkflowStateEscalation


class WorkflowTemplateStateForm(forms.ModelForm):
    class Meta:
        fields = ('initial', 'label', 'completion')
        model = WorkflowState
