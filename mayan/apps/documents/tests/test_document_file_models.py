from pathlib import Path

from ..events import (
    event_document_file_created, event_document_file_deleted,
    event_document_file_edited, event_document_version_created,
    event_document_version_page_created, event_document_version_page_deleted
)

from .base import GenericDocumentTestCase
from .literals import TEST_DOCUMENT_SMALL_CHECKSUM
from .mixins.document_file_mixins import DocumentFileTestMixin


class DocumentFileTestCase(DocumentFileTestMixin, GenericDocumentTestCase):
    def test_file_create(self):
        document_file_count = self._test_document.files.count()

        self._clear_events()

        self._upload_test_document_file(user=self._test_case_user)

        self.assertEqual(
            self._test_document.files.count(), document_file_count + 1
        )
        self.assertEqual(
            self._test_document.file_latest.checksum,
            TEST_DOCUMENT_SMALL_CHECKSUM
        )

        events = self._get_test_events()
        self.assertEqual(events.count(), 4)

        self.assertEqual(events[0].action_object, self._test_document)
        self.assertEqual(events[0].actor, self._test_case_user)
        self.assertEqual(events[0].target, self._test_document_file)
        self.assertEqual(events[0].verb, event_document_file_created.id)

        self.assertEqual(events[1].action_object, self._test_document)
        self.assertEqual(events[1].actor, self._test_case_user)
        self.assertEqual(events[1].target, self._test_document_file)
        self.assertEqual(events[1].verb, event_document_file_edited.id)

        self.assertEqual(events[2].action_object, self._test_document)
        self.assertEqual(events[2].actor, self._test_case_user)
        self.assertEqual(events[2].target, self._test_document_version)
        self.assertEqual(events[2].verb, event_document_version_created.id)

        self.assertEqual(
            events[3].action_object, self._test_document_version
        )
        self.assertEqual(events[3].actor, self._test_case_user)
        self.assertEqual(events[3].target, self._test_document_version_page)
        self.assertEqual(
            events[3].verb, event_document_version_page_created.id
        )

    def test_document_file_delete(self):
        document_file_count = self._test_document.files.count()

        self._clear_events()

        self._test_document_file.delete(user=self._test_case_user)

        self.assertEqual(
            self._test_document.files.count(), document_file_count - 1
        )

        events = self._get_test_events()
        self.assertEqual(events.count(), 2)

        self.assertEqual(events[0].action_object, None)
        self.assertEqual(events[0].actor, self._test_case_user)
        self.assertEqual(events[0].target, self._test_document_version)
        self.assertEqual(
            events[0].verb, event_document_version_page_deleted.id
        )

        self.assertEqual(events[1].action_object, None)
        self.assertEqual(events[1].actor, self._test_case_user)
        self.assertEqual(events[1].target, self._test_document)
        self.assertEqual(
            events[1].verb, event_document_file_deleted.id
        )

    def test_document_file_filename_extraction(self):
        """
        Ensure only the filename is stored and not the entire path of the
        uploaded document file.
        """
        self.assertEqual(
            Path(self._test_document_file.filename).name,
            self._test_document_file.filename
        )

    def test_document_first_file_filename(self):
        """
        Ensure the filename of the first document is the same as the document
        label.
        """
        self.assertEqual(
            self._test_document_file.filename, self._test_document.label
        )

    def test_method_get_absolute_url(self):
        self._clear_events()

        self.assertTrue(
            self._test_document.file_latest.get_absolute_url()
        )

        events = self._get_test_events()
        self.assertEqual(events.count(), 0)
