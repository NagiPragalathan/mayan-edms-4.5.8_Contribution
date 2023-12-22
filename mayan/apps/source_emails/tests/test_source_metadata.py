from mayan.apps.documents.events import (
    event_document_created, event_document_file_created,
    event_document_file_edited, event_document_version_created,
    event_document_version_page_created
)
from mayan.apps.documents.models.document_models import Document
from mayan.apps.documents.tests.base import GenericDocumentTestCase

from .literals import (
    TEST_EMAIL_NO_CONTENT_TYPE, TEST_EMAIL_NO_CONTENT_TYPE_DATE,
    TEST_EMAIL_NO_CONTENT_TYPE_DEVELIVERED_TO,
    TEST_EMAIL_NO_CONTENT_TYPE_FROM, TEST_EMAIL_NO_CONTENT_TYPE_MESSAGE_ID,
    TEST_EMAIL_NO_CONTENT_TYPE_RECEIVED, TEST_EMAIL_NO_CONTENT_TYPE_STRING,
    TEST_EMAIL_NO_CONTENT_TYPE_SUBJECT, TEST_EMAIL_NO_CONTENT_TYPE_TO
)
from .mixins import EmailSourceTestMixin


class EmailSourceBackendDocumentUploadSourceMetadataTestCase(
    EmailSourceTestMixin, GenericDocumentTestCase
):
    _test_source_create_auto = False
    auto_upload_test_document = False

    def test_no_content_type_source_metadata(self):
        self._test_source_content = TEST_EMAIL_NO_CONTENT_TYPE
        self._test_source_create(
            extra_data={
                'store_body': True
            }
        )

        self._clear_events()

        self._execute_test_source_action(action_name='document_upload')

        test_document = Document.objects.first()
        test_document_file = test_document.file_latest
        test_document_version = test_document.version_active
        test_document_version_page = test_document_version.pages.first()

        self.assertTrue(
            TEST_EMAIL_NO_CONTENT_TYPE_STRING in test_document_file.open().read()
        )

        self.assertEqual(test_document_file.source_metadata.count(), 8)

        self.assertEqual(
            test_document_file.source_metadata.get(key='email_date').value,
            TEST_EMAIL_NO_CONTENT_TYPE_DATE
        )
        self.assertEqual(
            test_document_file.source_metadata.get(key='email_delivered_to').value,
            TEST_EMAIL_NO_CONTENT_TYPE_DEVELIVERED_TO
        )
        self.assertEqual(
            test_document_file.source_metadata.get(key='email_from').value,
            TEST_EMAIL_NO_CONTENT_TYPE_FROM
        )
        self.assertEqual(
            test_document_file.source_metadata.get(key='email_message_id').value,
            TEST_EMAIL_NO_CONTENT_TYPE_MESSAGE_ID
        )
        self.assertEqual(
            test_document_file.source_metadata.get(key='email_received').value,
            TEST_EMAIL_NO_CONTENT_TYPE_RECEIVED
        )
        self.assertEqual(
            test_document_file.source_metadata.get(key='email_subject').value,
            TEST_EMAIL_NO_CONTENT_TYPE_SUBJECT
        )
        self.assertEqual(
            test_document_file.source_metadata.get(key='email_to').value,
            TEST_EMAIL_NO_CONTENT_TYPE_TO
        )
        self.assertEqual(
            test_document_file.source_metadata.get(key='source_id').value,
            str(self._test_source.pk)
        )

        events = self._get_test_events()
        self.assertEqual(events.count(), 5)

        self.assertEqual(events[0].action_object, self._test_document_type)
        self.assertEqual(events[0].actor, test_document)
        self.assertEqual(events[0].target, test_document)
        self.assertEqual(events[0].verb, event_document_created.id)

        self.assertEqual(events[1].action_object, test_document)
        self.assertEqual(events[1].actor, test_document_file)
        self.assertEqual(events[1].target, test_document_file)
        self.assertEqual(events[1].verb, event_document_file_created.id)

        self.assertEqual(events[2].action_object, test_document)
        self.assertEqual(events[2].actor, test_document_file)
        self.assertEqual(events[2].target, test_document_file)
        self.assertEqual(events[2].verb, event_document_file_edited.id)

        self.assertEqual(events[3].action_object, test_document)
        self.assertEqual(events[3].actor, test_document_version)
        self.assertEqual(events[3].target, test_document_version)
        self.assertEqual(events[3].verb, event_document_version_created.id)

        self.assertEqual(events[4].action_object, test_document_version)
        self.assertEqual(events[4].actor, test_document_version_page)
        self.assertEqual(events[4].target, test_document_version_page)
        self.assertEqual(
            events[4].verb, event_document_version_page_created.id
        )
