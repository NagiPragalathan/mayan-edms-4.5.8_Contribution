import hashlib

from django.conf import settings
from django.core import serializers
from django.utils.translation import ugettext_lazy as _

from mayan.apps.templating.classes import Template


class WorkflowStateActionBusinessLogicMixin:
    def get_hash(self):
        return hashlib.sha256(
            string=serializers.serialize(
                format='json', queryset=(self,)
            ).encode()
        ).hexdigest()

    def evaluate_condition(self, workflow_instance):
        if self.has_condition():
            template = Template(template_string=self.condition)
            context = {'workflow_instance': workflow_instance}
            return template.render(context=context).strip()
        else:
            return True

    def execute(self, context, workflow_instance):
        if self.evaluate_condition(workflow_instance=workflow_instance):
            context.update(
                {
                    'workflow_instance': workflow_instance
                }
            )

            try:
                backend_instance = self.get_backend_instance()
                backend_instance.execute(context=context)
            except Exception as exception:
                self.error_log.create(
                    text='{}; {}'.format(
                        exception.__class__.__name__, exception
                    )
                )

                if settings.DEBUG or settings.TESTING:
                    raise
            else:
                queryset_error_log = self.error_log.all()
                queryset_error_log.delete()

    def has_condition(self):
        return self.condition.strip()

    has_condition.help_text = _(
        'The state action will be executed, depending on the condition '
        'return value.'
    )
    has_condition.short_description = _('Has a condition?')
