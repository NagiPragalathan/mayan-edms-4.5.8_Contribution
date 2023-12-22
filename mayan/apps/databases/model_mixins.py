import logging

from django.db import models
from django.utils.translation import ugettext_lazy as _

from mayan.apps.templating.classes import Template

logger = logging.getLogger(name=__name__)


class ExtraDataModelMixin:
    def __init__(self, *args, **kwargs):
        _instance_extra_data = kwargs.pop(
            '_instance_extra_data', {}
        )
        result = super().__init__(*args, **kwargs)
        for key, value in _instance_extra_data.items():
            setattr(self, key, value)

        return result


class ModelMixinConditionField(models.Model):
    condition = models.TextField(
        blank=True, help_text=_(
            'The condition that will determine if this object '
            'is executed or not. Conditions that do not return any value, '
            'that return the Python logical None, or an empty string (\'\') '
            'are considered to be logical false, any other value is '
            'considered to be the logical true.'
        ), verbose_name=_('Condition')
    )

    class Meta:
        abstract = True

    def evaluate_condition(self, context):
        if self.has_condition():
            result = Template(template_string=self.condition).render(
                context=context
            ).strip()
            return result
        else:
            return True

    def has_condition(self):
        if self.condition.strip():
            return True
        else:
            return False
    has_condition.help_text = _(
        'The object will be executed, depending on the condition '
        'return value.'
    )
    has_condition.short_description = _('Has a condition?')


class ValueChangeModelMixin:
    @classmethod
    def from_db(cls, db, field_names, values):
        new = super().from_db(db=db, field_names=field_names, values=values)
        new._values_previous = dict(zip(field_names, values))
        return new

    def __init__(self, *args, **kwargs):
        self._values_previous = kwargs
        super().__init__(*args, **kwargs)

    def _get_field_previous_value(self, field):
        return self._values_previous[field]

    def _has_field_changed(self, field):
        if self._state.adding:
            if getattr(self, field) != self._values_previous[field]:
                return True

        return False
