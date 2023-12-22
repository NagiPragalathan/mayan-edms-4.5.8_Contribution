import logging

import yaml

from django.utils.translation import ugettext_lazy as _
from django.core.exceptions import ValidationError

from mayan.apps.common.serialization import yaml_load
from mayan.apps.common.utils import parse_range
from mayan.apps.document_states.classes import WorkflowAction

from .models import ObjectLayer
from .transformations import BaseTransformation

__all__ = ('TransformationAddAction',)
logger = logging.getLogger(name=__name__)


class TransformationAddAction(WorkflowAction):
    form_field_widgets = {
        'transformation_class': {
            'class': 'django.forms.widgets.Select', 'kwargs': {
                'attrs': {'class': 'select2'}
            }
        },
        'transformation_arguments': {
            'class': 'django.forms.widgets.Textarea', 'kwargs': {
                'attrs': {'rows': 5}
            }
        }
    }
    form_fields = {
        'pages': {
            'label': _('Pages'),
            'class': 'django.forms.CharField', 'kwargs': {
                'help_text': _(
                    'Pages to which the new transformations will be added. '
                    'Separate by commas and/or use a dashes for a ranges. '
                    'Leave blank to select all pages.'
                ), 'required': False
            }
        },
        'transformation_class': {
            'label': _('Transformation class'),
            'class': 'django.forms.ChoiceField', 'kwargs': {
                'choices': BaseTransformation.get_transformation_choices(
                    group_by_layer=True
                ), 'help_text': _(
                    'Type of transformation to add.'
                ), 'required': True
            }
        },
        'transformation_arguments': {
            'label': _('Transformation arguments'),
            'class': 'django.forms.CharField', 'kwargs': {
                'help_text': _(
                    'Enter the arguments for the transformation as a YAML '
                    'dictionary. ie: {"degrees": 180}'
                ), 'required': False
            }
        }
    }
    label = _('Add transformation')

    @classmethod
    def clean(cls, form_data, request):
        try:
            yaml_load(
                stream=form_data['action_data']['transformation_arguments']
            )
        except yaml.YAMLError:
            raise ValidationError(
                message=_(
                    '"%s" not a valid entry.'
                ) % form_data['action_data']['transformation_arguments']
            )

        return form_data

    @classmethod
    def get_form_fieldsets(cls):
        fieldsets = super().get_form_fieldsets()

        fieldsets += (
            (
                _('Objects'), {
                    'fields': ('pages',)
                }
            ),
            (
                _('Transformations'), {
                    'fields': (
                        'transformation_class', 'transformation_arguments',
                    )
                }
            ),
        )
        return fieldsets

    def execute(self, context):
        if self.kwargs['pages']:
            page_range = parse_range(
                range_string=self.kwargs['pages']
            )
            queryset = context['workflow_instance'].document.pages.filter(
                page_number__in=page_range
            )
        else:
            queryset = context['workflow_instance'].document.pages.all()

        transformation_class = BaseTransformation.get(
            name=self.kwargs['transformation_class']
        )
        layer = transformation_class.get_assigned_layer()

        for document_page in queryset.all():
            object_layer, created = ObjectLayer.objects.get_for(
                layer=layer, obj=document_page
            )
            object_layer.transformations.create(
                arguments=self.kwargs['transformation_arguments'],
                name=transformation_class.name
            )
