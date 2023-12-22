from unittest import mock

from mayan.apps.documents.events import (
    event_document_created, event_document_file_created,
    event_document_version_created
)
from mayan.apps.documents.models.document_models import Document
from mayan.apps.documents.tests.base import GenericDocumentTestCase

from .mixins import PeriodicSourceBackendTestMixin


class SourceBackendCallbackTestCase(
    PeriodicSourceBackendTestMixin, GenericDocumentTestCase
):
    auto_upload_test_document = False

    @mock.patch(
        target='mayan.apps.sources.models.Source.callback_post_document_create'
    )
    def test_callback_post_document_create_on_document_upload(
        self, mocked_source_method
    ):
        self._silence_logger(name='mayan.apps.converter.backends')

        document_count = Document.objects.count()

        self._clear_events()

        self._execute_test_source_action(action_name='document_upload')

        self.assertEqual(Document.objects.count(), document_count + 1)

        self.assertEqual(mocked_source_method.call_count, 1)

        events = self._get_test_events()
        self.assertEqual(events.count(), 3)

        test_document = Document.objects.first()
        test_document_file = test_document.file_latest
        test_document_version = test_document.version_active

        self.assertEqual(events[0].action_object, self._test_document_type)
        self.assertEqual(events[0].actor, test_document)
        self.assertEqual(events[0].target, test_document)
        self.assertEqual(events[0].verb, event_document_created.id)

        self.assertEqual(events[1].action_object, test_document)
        self.assertEqual(events[1].actor, test_document_file)
        self.assertEqual(events[1].target, test_document_file)
        self.assertEqual(events[1].verb, event_document_file_created.id)

        self.assertEqual(events[2].action_object, test_document)
        self.assertEqual(events[2].actor, test_document_version)
        self.assertEqual(events[2].target, test_document_version)
        self.assertEqual(events[2].verb, event_document_version_created.id)

    @mock.patch(
        target='mayan.apps.sources.models.Source.callback_post_document_file_upload'
    )
    def test_callback_post_document_file_upload_on_document_upload(
        self, mocked_source_method
    ):
        self._silence_logger(name='mayan.apps.converter.backends')

        document_count = Document.objects.count()

        self._clear_events()

        self._execute_test_source_action(action_name='document_upload')

        self.assertEqual(Document.objects.count(), document_count + 1)

        self.assertEqual(mocked_source_method.call_count, 1)

        events = self._get_test_events()
        self.assertEqual(events.count(), 3)

        test_document = Document.objects.first()
        test_document_file = test_document.file_latest
        test_document_version = test_document.version_active

        self.assertEqual(events[0].action_object, self._test_document_type)
        self.assertEqual(events[0].actor, test_document)
        self.assertEqual(events[0].target, test_document)
        self.assertEqual(events[0].verb, event_document_created.id)

        self.assertEqual(events[1].action_object, test_document)
        self.assertEqual(events[1].actor, test_document_file)
        self.assertEqual(events[1].target, test_document_file)
        self.assertEqual(events[1].verb, event_document_file_created.id)

        self.assertEqual(events[2].action_object, test_document)
        self.assertEqual(events[2].actor, test_document_version)
        self.assertEqual(events[2].target, test_document_version)
        self.assertEqual(events[2].verb, event_document_version_created.id)
