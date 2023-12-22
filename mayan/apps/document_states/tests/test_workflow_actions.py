import json
from unittest import mock

from mayan.apps.credentials.tests.mixins import StoredCredentialPasswordUsernameTestMixin
from mayan.apps.testing.tests.base import BaseTestCase, GenericViewTestCase
from mayan.apps.testing.tests.mixins import TestServerTestCaseMixin
from mayan.apps.testing.tests.mocks import request_method_factory

from ..literals import WORKFLOW_ACTION_ON_ENTRY
from ..models.workflow_models import Workflow
from ..models.workflow_instance_models import WorkflowInstance
from ..permissions import permission_workflow_template_edit
from ..workflow_actions import (
    DocumentPropertiesEditAction, DocumentWorkflowLaunchAction, HTTPAction
)

from .literals import (
    TEST_DOCUMENT_EDIT_WORKFLOW_TEMPLATE_STATE_ACTION_DOTTED_PATH,
    TEST_DOCUMENT_EDIT_WORKFLOW_TEMPLATE_STATE_ACTION_TEXT_LABEL,
    TEST_DOCUMENT_EDIT_WORKFLOW_TEMPLATE_STATE_ACTION_TEXT_DESCRIPTION,
    TEST_DOCUMENT_EDIT_WORKFLOW_TEMPLATE_STATE_ACTION_TEXT_DATA,
    TEST_DOCUMENT_EDIT_WORKFLOW_TEMPLATE_STATE_ACTION_TEMPLATE_DATA,
    TEST_HEADERS_AUTHENTICATION_KEY, TEST_HEADERS_AUTHENTICATION_VALUE,
    TEST_HEADERS_KEY, TEST_HEADERS_JSON, TEST_HEADERS_JSON_TEMPLATE,
    TEST_HEADERS_JSON_TEMPLATE_KEY, TEST_HEADERS_VALUE, TEST_PAYLOAD_JSON,
    TEST_PAYLOAD_TEMPLATE_DOCUMENT_LABEL, TEST_SERVER_USERNAME,
    TEST_SERVER_PASSWORD
)
from .mixins.workflow_template_state_action_mixins import (
    WorkflowTemplateStateActionLaunchViewTestMixin,
    WorkflowTemplateStateActionTestMixin,
    WorkflowTemplateStateActionViewTestMixin
)
from .mixins.workflow_template_transition_mixins import WorkflowTemplateTransitionTestMixin


class HTTPWorkflowActionTestCase(
    TestServerTestCaseMixin, WorkflowTemplateStateActionTestMixin,
    GenericViewTestCase
):
    auto_add_test_view = True

    @mock.patch('requests.sessions.Session.get_adapter')
    def test_http_post_action_simple(self, mock_object):
        mock_object.side_effect = request_method_factory(test_case=self)

        self._execute_workflow_template_state_action(
            klass=HTTPAction, kwargs={
                'method': 'POST',
                'url': self.testserver_url
            }
        )

        self.assertFalse(self.test_view_request is None)

    @mock.patch('requests.sessions.Session.get_adapter')
    def test_http_post_action_payload_simple(self, mock_object):
        mock_object.side_effect = request_method_factory(test_case=self)

        self._execute_workflow_template_state_action(
            klass=HTTPAction, kwargs={
                'method': 'POST',
                'payload': TEST_PAYLOAD_JSON,
                'url': self.testserver_url
            }
        )

        self.assertEqual(
            json.loads(s=self.test_view_request.body),
            {'label': 'label'}
        )

    @mock.patch('requests.sessions.Session.get_adapter')
    def test_http_post_action_payload_template(self, mock_object):
        self._create_test_document_stub()

        mock_object.side_effect = request_method_factory(test_case=self)

        self._execute_workflow_template_state_action(
            klass=HTTPAction, kwargs={
                'method': 'POST',
                'payload': TEST_PAYLOAD_TEMPLATE_DOCUMENT_LABEL,
                'url': self.testserver_url
            }
        )

        self.assertEqual(
            json.loads(s=self.test_view_request.body),
            {'label': self._test_document.label}
        )

    @mock.patch('requests.sessions.Session.get_adapter')
    def test_http_post_action_headers_simple(self, mock_object):
        mock_object.side_effect = request_method_factory(test_case=self)

        self._execute_workflow_template_state_action(
            klass=HTTPAction, kwargs={
                'method': 'POST',
                'headers': TEST_HEADERS_JSON,
                'url': self.testserver_url
            }
        )

        self.assertTrue(
            TEST_HEADERS_KEY in self.test_view_request.META,
        )
        self.assertEqual(
            self.test_view_request.META[TEST_HEADERS_KEY], TEST_HEADERS_VALUE
        )

    @mock.patch('requests.sessions.Session.get_adapter')
    def test_http_post_action_headers_template(self, mock_object):
        self._create_test_document_stub()

        mock_object.side_effect = request_method_factory(test_case=self)

        self._execute_workflow_template_state_action(
            klass=HTTPAction, kwargs={
                'method': 'POST',
                'headers': TEST_HEADERS_JSON_TEMPLATE,
                'url': self.testserver_url
            }
        )
        self.assertTrue(
            TEST_HEADERS_JSON_TEMPLATE_KEY in self.test_view_request.META,
        )
        self.assertEqual(
            self.test_view_request.META[TEST_HEADERS_JSON_TEMPLATE_KEY],
            self._test_document.label
        )

    @mock.patch('requests.sessions.Session.get_adapter')
    def test_http_post_action_authentication(self, mock_object):
        mock_object.side_effect = request_method_factory(test_case=self)

        self._execute_workflow_template_state_action(
            klass=HTTPAction, kwargs={
                'method': 'POST',
                'password': TEST_SERVER_PASSWORD,
                'url': self.testserver_url,
                'username': TEST_SERVER_USERNAME,
            }
        )
        self.assertTrue(
            TEST_HEADERS_AUTHENTICATION_KEY in self.test_view_request.META,
        )
        self.assertEqual(
            self.test_view_request.META[TEST_HEADERS_AUTHENTICATION_KEY],
            TEST_HEADERS_AUTHENTICATION_VALUE
        )

    @mock.patch('requests.sessions.Session.get_adapter')
    def test_http_post_action_timeout_value_int(self, mock_object):
        mock_object.side_effect = request_method_factory(test_case=self)

        self._execute_workflow_template_state_action(
            klass=HTTPAction, kwargs={
                'method': 'POST',
                'timeout': '1',
                'url': self.testserver_url
            }
        )
        self.assertEqual(self.timeout, 1)

    @mock.patch('requests.sessions.Session.get_adapter')
    def test_http_post_action_timeout_value_float(self, mock_object):
        mock_object.side_effect = request_method_factory(test_case=self)

        self._execute_workflow_template_state_action(
            klass=HTTPAction, kwargs={
                'method': 'POST',
                'timeout': '1.5',
                'url': self.testserver_url
            }
        )
        self.assertEqual(self.timeout, 1.5)

    @mock.patch('requests.sessions.Session.get_adapter')
    def test_http_post_action_timeout_value_none(self, mock_object):
        mock_object.side_effect = request_method_factory(test_case=self)

        self._execute_workflow_template_state_action(
            klass=HTTPAction, kwargs={
                'method': 'POST',
                'url': self.testserver_url
            }
        )
        self.assertEqual(self.timeout, None)


class HTTPCredentialTemplateWorkflowActionTestCase(
    StoredCredentialPasswordUsernameTestMixin, TestServerTestCaseMixin,
    WorkflowTemplateStateActionTestMixin, GenericViewTestCase
):
    auto_add_test_view = True

    @mock.patch('requests.sessions.Session.get_adapter')
    def test_http_post_action_headers_template(self, mock_object):
        self._create_test_document_stub()

        mock_object.side_effect = request_method_factory(test_case=self)

        self._execute_workflow_template_state_action(
            klass=HTTPAction, kwargs={
                'headers': '{{"{}": "{}"}}'.format(
                    TEST_HEADERS_JSON_TEMPLATE_KEY, '{{ credential.password }}'
                ),
                'method': 'POST',
                'stored_credential_id': self._test_stored_credential.pk,
                'url': self.testserver_url
            }
        )
        self.assertTrue(
            TEST_HEADERS_JSON_TEMPLATE_KEY in self.test_view_request.META,
        )
        self.assertEqual(
            self.test_view_request.META[TEST_HEADERS_JSON_TEMPLATE_KEY],
            self._test_stored_credential._password
        )

    @mock.patch('requests.sessions.Session.get_adapter')
    def test_http_post_action_authentication(self, mock_object):
        mock_object.side_effect = request_method_factory(test_case=self)

        self._execute_workflow_template_state_action(
            klass=HTTPAction, kwargs={
                'method': 'POST',
                'password': '{{ credential.password }}',
                'stored_credential_id': self._test_stored_credential.pk,
                'url': self.testserver_url,
                'username': '{{ credential.username }}'
            }
        )
        self.assertTrue(
            TEST_HEADERS_AUTHENTICATION_KEY in self.test_view_request.META,
        )
        self.assertEqual(
            self.test_view_request.META[TEST_HEADERS_AUTHENTICATION_KEY],
            'Basic dGVzdF9jcmVkZW50aWFsX3VzZXJuYW1lOnRlc3RfY3JlZGVudGlhbF9wYXNzd29yZA=='
        )


class HTTPWorkflowActionViewTestCase(
    WorkflowTemplateStateActionViewTestMixin, GenericViewTestCase
):
    def test_http_workflow_state_action_create_post_view_no_permission(self):
        action_count = self._test_workflow_template_state.actions.count()

        response = self._request_test_workflow_template_state_action_create_post_view(
            backend_path='mayan.apps.document_states.workflow_actions.HTTPAction',
            extra_data={
                'method_template': 'POST', 'timeout_template': '0',
                'url_template': '127.0.0.1'
            }
        )
        self.assertEqual(response.status_code, 404)

        self._test_workflow_template_state.refresh_from_db()
        self.assertEqual(
            self._test_workflow_template_state.actions.count(), action_count
        )

    def test_http_workflow_state_action_create_post_view_with_access(self):
        self.grant_access(
            obj=self._test_workflow_template,
            permission=permission_workflow_template_edit
        )
        action_count = self._test_workflow_template_state.actions.count()

        response = self._request_test_workflow_template_state_action_create_post_view(
            backend_path='mayan.apps.document_states.workflow_actions.HTTPAction',
            extra_data={
                'method_template': 'POST', 'timeout_template': '0',
                'url_template': '127.0.0.1'
            }
        )
        self.assertEqual(response.status_code, 302)

        self._test_workflow_template_state.refresh_from_db()
        self.assertEqual(
            self._test_workflow_template_state.actions.count(), action_count + 1
        )


class DocumentPropertiesEditActionTestCase(
    WorkflowTemplateStateActionTestMixin,
    WorkflowTemplateTransitionTestMixin, BaseTestCase
):
    def test_document_properties_edit_action_field_literals(self):
        test_values = self._model_instance_to_dictionary(
            instance=self._test_document
        )

        self._execute_workflow_template_state_action(
            klass=DocumentPropertiesEditAction,
            kwargs=TEST_DOCUMENT_EDIT_WORKFLOW_TEMPLATE_STATE_ACTION_TEXT_DATA
        )

        self._test_document.refresh_from_db()

        self.assertNotEqual(
            test_values, self._model_instance_to_dictionary(
                instance=self._test_document
            )
        )

    def test_document_properties_edit_action_field_templates(self):
        label = self._test_document.label

        self._execute_workflow_template_state_action(
            klass=DocumentPropertiesEditAction,
            kwargs=TEST_DOCUMENT_EDIT_WORKFLOW_TEMPLATE_STATE_ACTION_TEMPLATE_DATA
        )

        self.assertEqual(
            self._test_document.label,
            '{} new'.format(label)
        )
        self.assertEqual(
            self._test_document.description,
            label
        )

    def test_document_properties_edit_action_workflow_transition(self):
        self._create_test_workflow_template_state()
        self._create_test_workflow_template_transition()

        self._test_workflow_template_states[1].actions.create(
            backend_data=json.dumps(
                obj=TEST_DOCUMENT_EDIT_WORKFLOW_TEMPLATE_STATE_ACTION_TEXT_DATA
            ),
            backend_path=TEST_DOCUMENT_EDIT_WORKFLOW_TEMPLATE_STATE_ACTION_DOTTED_PATH,
            label='', when=WORKFLOW_ACTION_ON_ENTRY,
        )

        test_workflow_instance = self._test_document.workflows.first()
        test_workflow_instance.do_transition(
            transition=self._test_workflow_template_transition
        )

        self._test_document.refresh_from_db()

        self.assertEqual(
            self._test_document.label,
            TEST_DOCUMENT_EDIT_WORKFLOW_TEMPLATE_STATE_ACTION_TEXT_LABEL
        )
        self.assertEqual(
            self._test_document.description,
            TEST_DOCUMENT_EDIT_WORKFLOW_TEMPLATE_STATE_ACTION_TEXT_DESCRIPTION
        )


class DocumentWorkflowLaunchActionTestCase(
    WorkflowTemplateStateActionTestMixin, BaseTestCase
):
    def test_document_workflow_launch_action(self):
        self._create_test_workflow_template(
            add_test_document_type=True, auto_launch=False
        )
        self._create_test_workflow_template_state()

        workflow_count = self._test_document.workflows.count()

        self._execute_workflow_template_state_action(
            klass=DocumentWorkflowLaunchAction,
            kwargs={
                'workflows': Workflow.objects.exclude(pk=self._test_workflow_instance.workflow.pk)
            }
        )

        self.assertEqual(
            self._test_document.workflows.count(), workflow_count + 1
        )


class DocumentWorkflowLaunchActionViewTestCase(
    WorkflowTemplateStateActionLaunchViewTestMixin, GenericViewTestCase
):
    def test_document_workflow_launch_action_view_with_full_access(self):
        self._create_test_workflow_template(
            add_test_document_type=True, auto_launch=False
        )

        self._create_test_workflow_template(
            add_test_document_type=True, auto_launch=False
        )
        self._create_test_workflow_template_state()

        self.grant_access(
            obj=self._test_workflow_template,
            permission=permission_workflow_template_edit
        )

        action_count = self._test_workflow_template_state.actions.count()

        response = self._request_document_workflow_template_launch_action_create_view(
            extra_data={
                'workflows': self._test_workflow_templates[0].pk
            }
        )
        self.assertEqual(response.status_code, 302)

        self.assertEqual(
            self._test_workflow_template_state.actions.count(),
            action_count + 1
        )

    def test_document_workflow_launch_action_view_and_document_create_with_full_access(self):
        self._test_document.delete()  # Send test document to trash.
        self._test_document.delete()  # Delete test document.

        self._test_workflow_template.delete()  # Delete templates.
        self._test_workflow_templates = []  # Delete templates.

        self._create_test_workflow_template(
            add_test_document_type=True, auto_launch=False
        )

        self._create_test_workflow_template(
            add_test_document_type=True, auto_launch=True
        )
        self._create_test_workflow_template_state()
        self.grant_access(
            obj=self._test_workflow_template,
            permission=permission_workflow_template_edit
        )

        action_count = self._test_workflow_template_state.actions.count()
        workflow_instance_count = WorkflowInstance.objects.count()

        response = self._request_document_workflow_template_launch_action_create_view(
            extra_data={
                'workflows': self._test_workflow_templates[0].pk
            }
        )
        self.assertEqual(response.status_code, 302)

        self.assertEqual(
            self._test_workflow_template_state.actions.count(),
            action_count + 1
        )

        self._create_test_document_stub()

        self.assertEqual(
            WorkflowInstance.objects.count(), workflow_instance_count + 2
        )
