from mayan.apps.documents.tests.mixins.document_mixins import DocumentTestMixin

from ..models import StoredDriver

from .literals import (
    TEST_DOCUMENT_FILE_METADATA_KEY, TEST_DOCUMENT_FILE_METADATA_VALUE,
    TEST_STORED_DRIVER_INTERNAL_NAME, TEST_STORED_DRIVER_PATH
)


class DocumentTypeViewTestMixin:
    def _request_document_type_file_metadata_settings_view(self):
        return self.get(
            viewname='file_metadata:document_type_file_metadata_settings',
            kwargs={'document_type_id': self._test_document.document_type.pk}
        )

    def _request_document_type_file_metadata_submit_view(self):
        return self.post(
            viewname='file_metadata:document_type_file_metadata_submit', data={
                'document_type': self._test_document_type.pk,
            }
        )


class FileMetadataViewTestMixin:
    def _request_document_file_metadata_driver_list_view(self):
        return self.get(
            viewname='file_metadata:document_file_metadata_driver_list',
            kwargs={'document_file_id': self._test_document_file.pk}
        )

    def _request_document_file_metadata_list_view(self):
        return self.get(
            viewname='file_metadata:document_file_metadata_driver_attribute_list',
            kwargs={
                'document_file_driver_id': self.test_driver.pk
            }
        )

    def _request_document_file_metadata_single_submit_view(self):
        return self.post(
            viewname='file_metadata:document_file_metadata_single_submit',
            kwargs={'document_file_id': self._test_document_file.pk}
        )

    def _request_document_file_multiple_submit_view(self):
        return self.post(
            viewname='file_metadata:document_file_metadata_multiple_submit',
            data={
                'id_list': self._test_document_file.pk,
            }
        )


class StoredDriverTestMixin:
    _test_stored_driver_create_auto = True

    def setUp(self):
        super().setUp()

        if self._test_stored_driver_create_auto:
            self._test_stored_driver_create()

    def _test_stored_driver_create(self):
        self._test_stored_driver = StoredDriver.objects.create(
            driver_path=TEST_STORED_DRIVER_PATH,
            internal_name=TEST_STORED_DRIVER_INTERNAL_NAME
        )


class FileMetadataTestMixin(DocumentTestMixin, StoredDriverTestMixin):
    _test_document_file_metadata_create_auto = True

    def setUp(self):
        super().setUp()

        if self._test_document_file_metadata_create_auto:
            self._test_document_file_metadata_create()

    def _test_document_file_metadata_create(self):
        self._test_document_file_driver_entry, created = self._test_document_file.file_metadata_drivers.get_or_create(
            driver=self._test_stored_driver
        )

        self._test_document_file_metadata = self._test_document_file_driver_entry.entries.create(
            key=TEST_DOCUMENT_FILE_METADATA_KEY,
            value=TEST_DOCUMENT_FILE_METADATA_VALUE
        )

        self._test_document_file_metadata_path = '{}__{}'.format(
            self._test_document_file_driver_entry.driver.internal_name,
            self._test_document_file_metadata.key
        )
