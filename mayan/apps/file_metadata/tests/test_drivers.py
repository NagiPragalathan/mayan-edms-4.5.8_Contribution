from mayan.apps.common.tests.literals import TEST_ARCHIVE_MSG_STRANGE_DATE_PATH
from mayan.apps.documents.tests.base import GenericDocumentTestCase
from mayan.apps.documents.tests.literals import TEST_FILE_PDF_FILENAME

from .literals import (
    TEST_PDF_FILE_METADATA_DOTTED_NAME, TEST_PDF_FILE_METADATA_VALUE,
    TEST_MSG_FILE_METADATA_DOTTED_NAME_SUBJECT,
    TEST_MSG_FILE_METADATA_DOTTED_NAME_TO,
    TEST_MSG_FILE_METADATA_VALUE_SUBJECT, TEST_MSG_FILE_METADATA_VALUE_TO
)


class EXIFToolDriverTestCase(GenericDocumentTestCase):
    _test_document_filename = TEST_FILE_PDF_FILENAME

    def test_driver_entries(self):
        self._test_document.submit_for_file_metadata_processing()

        value = self._test_document.file_latest.get_file_metadata(
            dotted_name=TEST_PDF_FILE_METADATA_DOTTED_NAME
        )
        self.assertEqual(value, TEST_PDF_FILE_METADATA_VALUE)


class ExtractMSGDriverTestCase(GenericDocumentTestCase):
    _test_document_filename = TEST_ARCHIVE_MSG_STRANGE_DATE_PATH

    def test_driver_entries(self):
        self._test_document.submit_for_file_metadata_processing()

        value_subject = self._test_document.file_latest.get_file_metadata(
            dotted_name=TEST_MSG_FILE_METADATA_DOTTED_NAME_SUBJECT
        )
        self.assertEqual(value_subject, TEST_MSG_FILE_METADATA_VALUE_SUBJECT)

        value_to = self._test_document.file_latest.get_file_metadata(
            dotted_name=TEST_MSG_FILE_METADATA_DOTTED_NAME_TO
        )
        self.assertEqual(value_to, TEST_MSG_FILE_METADATA_VALUE_TO)
