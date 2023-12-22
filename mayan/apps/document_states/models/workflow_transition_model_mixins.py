import hashlib

from django.core import serializers
from django.utils.translation import ugettext_lazy as _

from mayan.apps.common.serialization import yaml_load
from mayan.apps.templating.classes import Template


class WorkflowTransitionBusinessLogicMixin:
    def evaluate_condition(self, workflow_instance):
        if self.has_condition():
            return Template(template_string=self.condition).render(
                context={'workflow_instance': workflow_instance}
            ).strip()
        else:
            return True

    def get_field_display(self):
        field_list = [
            str(field) for field in self.fields.all()
        ]
        field_list.sort()

        return ', '.join(field_list)

    get_field_display.short_description = _('Fields')

    def get_hash(self):
        result = hashlib.sha256(
            string=serializers.serialize(
                format='json', queryset=(self,)
            ).encode()
        )
        for trigger_event in self.trigger_events.all():
            result.update(trigger_event.get_hash().encode())

        for field in self.fields.all():
            result.update(
                field.get_hash().encode()
            )

        return result.hexdigest()

    def has_condition(self):
        return self.condition.strip()
    has_condition.help_text = _(
        'The transition will be available, depending on the condition '
        'return value.'
    )
    has_condition.short_description = _('Has a condition?')


class WorkflowTransitionFieldBusinessLogicMixin:
    def get_hash(self):
        return hashlib.sha256(
            string=serializers.serialize(
                format='json', queryset=(self,)
            ).encode()
        ).hexdigest()

    def get_widget_kwargs(self):
        return yaml_load(
            stream=self.widget_kwargs or '{}'
        )


class WorkflowTransitionTriggerEventBusinessLogicMixin:
    def get_hash(self):
        return hashlib.sha256(
            string=serializers.serialize(
                format='json', queryset=(self,)
            ).encode()
        ).hexdigest()
