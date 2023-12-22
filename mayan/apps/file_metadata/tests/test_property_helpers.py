from mayan.apps.common.tests.mixins import PropertyHelperTestMixin
from mayan.apps.testing.tests.base import BaseTestCase

from .mixins import FileMetadataTestMixin


class DocumentPropertyHelperTestCase(
    FileMetadataTestMixin, PropertyHelperTestMixin, BaseTestCase
):
    def test_basic(self):
        self._clear_events()

        self.assertEqual(
            getattr(
                self._test_document.file_metadata_value_of,
                self._test_document_file_metadata_path
            ), self._test_document_file_metadata.value
        )

        events = self._get_test_events()
        self.assertEqual(events.count(), 0)

    def test_no_file(self):
        self._test_document_file.delete()

        self._clear_events()

        self.assertEqual(
            getattr(
                self._test_document.file_metadata_value_of,
                self._test_document_file_metadata_path
            ), None
        )

        events = self._get_test_events()
        self.assertEqual(events.count(), 0)

    def test_no_source_metadata(self):
        self._test_document_file_metadata.delete()

        self._clear_events()

        self.assertEqual(
            getattr(
                self._test_document.file_metadata_value_of,
                self._test_document_file_metadata_path
            ), None
        )

        events = self._get_test_events()
        self.assertEqual(events.count(), 0)

    def test_wrong_source_metadata_name(self):
        self._test_document_file_metadata.delete()

        self._clear_events()

        self.assertEqual(
            getattr(
                self._test_document.file_metadata_value_of,
                'invalid'
            ), None
        )

        events = self._get_test_events()
        self.assertEqual(events.count(), 0)


class DocumentFilePropertyHelperTestCase(
    FileMetadataTestMixin, PropertyHelperTestMixin, BaseTestCase
):
    def test_basic(self):
        self._clear_events()

        self.assertEqual(
            getattr(
                self._test_document_file.file_metadata_value_of,
                self._test_document_file_metadata_path
            ), self._test_document_file_metadata.value
        )

        events = self._get_test_events()
        self.assertEqual(events.count(), 0)

    def test_no_source_metadata(self):
        self._test_document_file_metadata.delete()

        self._clear_events()

        self.assertEqual(
            getattr(
                self._test_document_file.file_metadata_value_of,
                self._test_document_file_metadata_path
            ), None
        )

        events = self._get_test_events()
        self.assertEqual(events.count(), 0)

    def test_wrong_source_metadata_name(self):
        self._test_document_file_metadata.delete()

        self._clear_events()

        self.assertEqual(
            getattr(
                self._test_document_file.file_metadata_value_of,
                'invalid'
            ), None
        )

        events = self._get_test_events()
        self.assertEqual(events.count(), 0)
