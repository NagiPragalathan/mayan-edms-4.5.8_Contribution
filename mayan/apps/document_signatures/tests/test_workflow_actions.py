import json

from mayan.apps.django_gpg.tests.literals import TEST_KEY_PRIVATE_PASSPHRASE
from mayan.apps.django_gpg.tests.mixins import KeyTestMixin
from mayan.apps.document_states.literals import WORKFLOW_ACTION_ON_ENTRY
from mayan.apps.document_states.permissions import permission_workflow_template_edit
from mayan.apps.document_states.tests.mixins.workflow_template_state_action_mixins import (
    WorkflowTemplateStateActionTestMixin,
    WorkflowTemplateStateActionViewTestMixin
)
from mayan.apps.documents.tests.base import BaseTestCase, GenericViewTestCase

from ..models import DetachedSignature, EmbeddedSignature
from ..workflow_actions import (
    DocumentSignatureDetachedAction, DocumentSignatureEmbeddedAction
)

from .literals import (
    DOCUMENT_SIGNATURE_DETACHED_ACTION_CLASS_PATH,
    DOCUMENT_SIGNATURE_EMBEDDED_ACTION_CLASS_PATH
)


class DocumentSignatureWorkflowActionTestCase(
    KeyTestMixin, WorkflowTemplateStateActionTestMixin, BaseTestCase
):
    def test_document_signature_detached_action(self):
        self._test_document.delete()
        self._test_document.delete()

        self._upload_test_document()
        self._create_test_key_private()
        signature_count = DetachedSignature.objects.count()

        self._execute_workflow_template_state_action(
            klass=DocumentSignatureDetachedAction, kwargs={
                'key': self._test_key_private.pk,
                'passphrase': TEST_KEY_PRIVATE_PASSPHRASE
            }
        )
        self.assertNotEqual(
            signature_count, DetachedSignature.objects.count()
        )

    def test_document_signature_embedded_action(self):
        self._test_document.delete()
        self._test_document.delete()

        self._upload_test_document()
        self._create_test_key_private()
        signature_count = EmbeddedSignature.objects.count()

        self._execute_workflow_template_state_action(
            klass=DocumentSignatureEmbeddedAction, kwargs={
                'key': self._test_key_private.pk,
                'passphrase': TEST_KEY_PRIVATE_PASSPHRASE
            }
        )
        self.assertNotEqual(
            signature_count, EmbeddedSignature.objects.count()
        )


class DocumentSignatureWorkflowActionTransitionTestCase(
    KeyTestMixin, WorkflowTemplateStateActionTestMixin, GenericViewTestCase
):
    def test_document_signature_detached_action_via_workflow(self):
        self._test_document.delete()
        self._test_document.delete()

        self._create_test_workflow_template_state()
        self._create_test_workflow_template_transition()
        self._create_test_key_private()

        self._test_workflow_template_states[1].actions.create(
            backend_path='mayan.apps.document_signatures.workflow_actions.DocumentSignatureDetachedAction',
            backend_data=json.dumps(
                obj={
                    'key': self._test_key_private.pk,
                    'passphrase': TEST_KEY_PRIVATE_PASSPHRASE
                }
            ), label='test action', when=WORKFLOW_ACTION_ON_ENTRY,
            enabled=True
        )

        self._upload_test_document()
        self._test_workflow_instance = self._test_document.workflows.first()

        signature_count = DetachedSignature.objects.count()

        self._test_workflow_instance.do_transition(
            transition=self._test_workflow_template_transition
        )
        self.assertNotEqual(
            signature_count, DetachedSignature.objects.count()
        )

    def test_document_signature_embedded_action_via_workflow(self):
        self._test_document.delete()
        self._test_document.delete()

        self._create_test_workflow_template_state()
        self._create_test_workflow_template_transition()
        self._create_test_key_private()

        self._test_workflow_template_states[1].actions.create(
            backend_path='mayan.apps.document_signatures.workflow_actions.DocumentSignatureEmbeddedAction',
            backend_data=json.dumps(
                obj={
                    'key': self._test_key_private.pk,
                    'passphrase': TEST_KEY_PRIVATE_PASSPHRASE
                }
            ), label='test action', when=WORKFLOW_ACTION_ON_ENTRY,
            enabled=True
        )

        self._upload_test_document()
        self._test_workflow_instance = self._test_document.workflows.first()

        signature_count = EmbeddedSignature.objects.count()

        self._test_workflow_instance.do_transition(
            transition=self._test_workflow_template_transition
        )
        self.assertNotEqual(
            signature_count, EmbeddedSignature.objects.count()
        )


class DocumentSignatureWorkflowActionViewTestCase(
    KeyTestMixin, WorkflowTemplateStateActionViewTestMixin,
    GenericViewTestCase
):
    def test_document_signature_detached_action_create_view(self):
        self.grant_access(
            obj=self._test_workflow_template,
            permission=permission_workflow_template_edit
        )

        request = self._request_test_workflow_template_state_action_create_get_view(
            backend_path=DOCUMENT_SIGNATURE_DETACHED_ACTION_CLASS_PATH
        )
        self.assertEqual(request.status_code, 200)

    def test_document_signature_embedded_action_create_view(self):
        self.grant_access(
            obj=self._test_workflow_template,
            permission=permission_workflow_template_edit
        )

        request = self._request_test_workflow_template_state_action_create_get_view(
            backend_path=DOCUMENT_SIGNATURE_EMBEDDED_ACTION_CLASS_PATH
        )
        self.assertEqual(request.status_code, 200)
