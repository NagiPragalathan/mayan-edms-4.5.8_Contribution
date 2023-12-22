from django import forms
from django.utils.translation import ugettext_lazy as _

from ..models import WorkflowTransition


class WorkflowInstanceTransitionSelectForm(forms.Form):
    def __init__(self, user, workflow_instance, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.fields[
            'transition'
        ].queryset = workflow_instance.get_transition_choices(user=user)

    transition = forms.ModelChoiceField(
        help_text=_('Select a transition to execute in the next step.'),
        label=_('Transition'), queryset=WorkflowTransition.objects.none()
    )
