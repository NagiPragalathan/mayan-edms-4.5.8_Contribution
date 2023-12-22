import logging
import json

import requests

from django.utils.text import format_lazy
from django.utils.translation import ugettext_lazy as _

from mayan.apps.credentials.class_mixins import BackendMixinCredentialsOptional

from .classes import WorkflowAction
from .exceptions import WorkflowStateActionError
from .literals import (
    BASE_WORKFLOW_TEMPLATE_STATE_ACTION_HELP_TEXT,
    DEFAULT_HTTP_ACTION_TIMEOUT
)
from .models.workflow_instance_models import WorkflowInstance
from .models.workflow_models import Workflow
from .permissions import permission_workflow_tools
from .tasks import task_launch_workflow_for

logger = logging.getLogger(name=__name__)


class DocumentPropertiesEditAction(WorkflowAction):
    form_fields = {
        'document_label': {
            'label': _('Document label'),
            'class': 'mayan.apps.templating.fields.ModelTemplateField',
            'kwargs': {
                'initial_help_text': _(
                    format_lazy(
                        '{} {}',
                        _('The new label to be assigned to the document.'),
                        BASE_WORKFLOW_TEMPLATE_STATE_ACTION_HELP_TEXT
                    )
                ),
                'model': WorkflowInstance,
                'model_variable': 'workflow_instance',
                'required': False
            },
        }, 'document_description': {
            'label': _('Document description'),
            'class': 'mayan.apps.templating.fields.ModelTemplateField',
            'kwargs': {
                'initial_help_text': _(
                    format_lazy(
                        '{} {}',
                        _(
                            'The new description to be assigned to the '
                            'document.'
                        ), BASE_WORKFLOW_TEMPLATE_STATE_ACTION_HELP_TEXT
                    )
                ),
                'model': WorkflowInstance,
                'model_variable': 'workflow_instance',
                'required': False
            }
        }
    }
    label = _('Modify document properties')

    @classmethod
    def get_form_fieldsets(cls):
        fieldsets = super().get_form_fieldsets()

        fieldsets += (
            (
                _('Document properties'), {
                    'fields': ('document_label', 'document_description')
                },
            ),
        )
        return fieldsets

    def execute(self, context):
        self.document_label = self.kwargs.get('document_label')
        self.document_description = self.kwargs.get(
            'document_description'
        )
        new_label = None
        new_description = None

        if self.document_label:
            new_label = self.render_field(
                field_name='document_label', context=context
            )

        if self.document_description:
            new_description = self.render_field(
                field_name='document_description', context=context
            )

        if new_label or new_description:
            document = context['workflow_instance'].document
            document.label = new_label or document.label
            document.description = new_description or document.description

            document.save()


class DocumentWorkflowLaunchAction(WorkflowAction):
    form_field_widgets = {
        'workflows': {
            'class': 'django.forms.widgets.SelectMultiple', 'kwargs': {
                'attrs': {'class': 'select2'},
            }
        }
    }
    label = _('Launch workflows')

    @classmethod
    def get_form_fields(cls):
        fields = super().get_form_fields()

        workflow_template = cls.workflow_template_state.workflow

        workflows_union = Workflow.objects.filter(
            document_types__in=workflow_template.document_types.all()
        ).exclude(pk=workflow_template.pk).distinct()

        fields.update(
            {
                'workflows': {
                    'class': 'mayan.apps.views.fields.ModelFormFieldFilteredModelMultipleChoice',
                    'help_text': _(
                        'Additional workflows to launch for the document.'
                    ),
                    'kwargs': {
                        'source_queryset': workflows_union,
                        'permission': permission_workflow_tools
                    },
                    'label': _('Workflows'),
                    'required': True
                }
            }
        )

        return fields

    @classmethod
    def get_form_fieldsets(cls):
        fieldsets = super().get_form_fieldsets()

        fieldsets += (
            (
                _('Workflows'), {
                    'fields': ('workflows',)
                },
            ),
        )
        return fieldsets

    def execute(self, context):
        workflows = Workflow.objects.filter(
            pk__in=self.kwargs.get(
                'workflows', ()
            )
        )

        document = context['workflow_instance'].document

        for workflow in workflows:
            task_launch_workflow_for.apply_async(
                kwargs={
                    'document_id': document.pk,
                    'workflow_id': workflow.pk
                }
            )


class HTTPAction(BackendMixinCredentialsOptional, WorkflowAction):
    form_fields = {
        'url': {
            'label': _('URL'),
            'class': 'mayan.apps.templating.fields.ModelTemplateField',
            'kwargs': {
                'initial_help_text': _(
                    format_lazy(
                        '{} {}',
                        _('The URL to access.'),
                        BASE_WORKFLOW_TEMPLATE_STATE_ACTION_HELP_TEXT
                    )
                ),
                'model': WorkflowInstance,
                'model_variable': 'workflow_instance',
                'required': True
            },
        }, 'method': {
            'label': _('Method'),
            'class': 'mayan.apps.templating.fields.ModelTemplateField',
            'kwargs': {
                'initial_help_text': _(
                    format_lazy(
                        '{} {}',
                        _(
                            'The HTTP method to use for the request. '
                            'Typical choices are OPTIONS, HEAD, POST, GET, '
                            'PUT, PATCH, DELETE.'
                        ), BASE_WORKFLOW_TEMPLATE_STATE_ACTION_HELP_TEXT
                    )
                ),
                'model': WorkflowInstance,
                'model_variable': 'workflow_instance',
                'required': True
            }
        }, 'username': {
            'label': _('Username'),
            'class': 'mayan.apps.templating.fields.ModelTemplateField',
            'kwargs': {
                'initial_help_text': _(
                    format_lazy(
                        '{} {} {}',
                        _(
                            'Username to use for making the request with '
                            'HTTP Basic Auth.'
                        ), BASE_WORKFLOW_TEMPLATE_STATE_ACTION_HELP_TEXT,
                        _(
                            'The credential object is available as '
                            '{{ credential }}.'
                        )
                    )
                ),
                'max_length': 192,
                'model': WorkflowInstance,
                'model_variable': 'workflow_instance',
                'required': False
            },
        }, 'password': {
            'label': _('Password'),
            'class': 'mayan.apps.templating.fields.ModelTemplateField',
            'kwargs': {
                'initial_help_text': _(
                    format_lazy(
                        '{} {} {}',
                        _(
                            'Password to use for making the request with '
                            'HTTP Basic Auth.'
                        ), BASE_WORKFLOW_TEMPLATE_STATE_ACTION_HELP_TEXT,
                        _(
                            'The credential object is available as '
                            '{{ credential }}.'
                        )
                    )
                ),
                'max_length': 255,
                'model': WorkflowInstance,
                'model_variable': 'workflow_instance',
                'required': False
            },
        }, 'headers': {
            'label': _('Headers'),
            'class': 'mayan.apps.templating.fields.ModelTemplateField',
            'kwargs': {
                'initial_help_text': _(
                    format_lazy(
                        '{} {} {}',
                        _(
                            'Headers to send with the HTTP request. Must '
                            'be in JSON format.'
                        ), BASE_WORKFLOW_TEMPLATE_STATE_ACTION_HELP_TEXT,
                        _(
                            'The credential object is available as '
                            '{{ credential }}.'
                        )
                    )
                ),
                'model': WorkflowInstance,
                'model_variable': 'workflow_instance',
                'required': False
            }
        }, 'payload': {
            'label': _('Payload'),
            'class': 'mayan.apps.templating.fields.ModelTemplateField',
            'kwargs': {
                'initial_help_text': _(
                    format_lazy(
                        '{} {}',
                        _('A JSON document to include in the request.'),
                        BASE_WORKFLOW_TEMPLATE_STATE_ACTION_HELP_TEXT
                    )
                ),
                'model': WorkflowInstance,
                'model_variable': 'workflow_instance',
                'required': False
            }
        }, 'timeout': {
            'label': _('Timeout'),
            'class': 'mayan.apps.templating.fields.ModelTemplateField',
            'default': DEFAULT_HTTP_ACTION_TIMEOUT,
            'kwargs': {
                'initial_help_text': _(
                    format_lazy(
                        '{} {}',
                        _('Time in seconds to wait for a response.'),
                        BASE_WORKFLOW_TEMPLATE_STATE_ACTION_HELP_TEXT
                    )
                ),
                'model': WorkflowInstance,
                'model_variable': 'workflow_instance',
                'required': True
            }
        }

    }
    label = _('Perform an HTTP request')
    previous_dotted_paths = (
        'mayan.apps.document_states.workflow_actions.HTTPPostAction',
    )

    @classmethod
    def get_form_fieldsets(cls):
        fieldsets = super().get_form_fieldsets()

        fieldsets += (
            (
                _('HTTP'), {
                    'fields': (
                        'url', 'username', 'password', 'headers', 'timeout',
                        'method', 'payload'
                    )
                },
            ),
        )
        return fieldsets

    def render_field_load(self, field_name, context):
        """
        Method to perform a template render and subsequent JSON load.
        """
        render_result = self.render_field(
            field_name=field_name, context=context
        ) or '{}'

        try:
            load_result = json.loads(s=render_result, strict=False)
        except Exception as exception:
            raise WorkflowStateActionError(
                _('%(field_name)s JSON error: %(exception)s') % {
                    'field_name': field_name, 'exception': exception
                }
            )

        logger.debug('load result: %s', load_result)

        return load_result

    def execute(self, context):
        authentication_context = context.copy()

        credential = self.get_credential()
        if credential:
            authentication_context['credential'] = credential

        headers = self.render_field_load(
            field_name='headers', context=authentication_context
        )
        method = self.render_field(field_name='method', context=context)
        password = self.render_field(
            field_name='password', context=authentication_context
        )
        payload = self.render_field_load(
            field_name='payload', context=context
        )
        timeout = self.render_field(field_name='timeout', context=context)
        url = self.render_field(field_name='url', context=context)
        username = self.render_field(
            field_name='username', context=authentication_context
        )

        if '.' in timeout:
            timeout = float(timeout)
        elif timeout:
            timeout = int(timeout)
        else:
            timeout = None

        authentication = None
        if username or password:
            authentication = requests.auth.HTTPBasicAuth(
                password=password, username=username
            )

        requests.request(
            auth=authentication, headers=headers, json=payload,
            method=method, timeout=timeout, url=url
        )
