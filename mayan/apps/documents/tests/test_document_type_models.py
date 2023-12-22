from ..classes import OriginalDocumentFilenameGenerator, UUIDDocumentFilenameGenerator, UUIDPlusOriginalFilename
from ..models import TrashedDocument, Document, DocumentType

from .base import GenericDocumentTestCase


class DocumentTypeModelFilenameGeneratorTestCase(GenericDocumentTestCase):
    auto_upload_test_document = False

    def test_original_filename_generator(self):
        self._test_document_type.filename_generator_backend = OriginalDocumentFilenameGenerator.name
        self._test_document_type.save()
        self._upload_test_document()
        self.assertEqual(
            str(self._test_document.file_latest.file),
            self._test_document_filename
        )

    def test_uuid_filename_gnerator(self):
        self._test_document_type.filename_generator_backend = UUIDDocumentFilenameGenerator.name
        self._test_document_type.save()
        self._upload_test_document()
        self.assertNotEqual(
            str(self._test_document.file_latest.file),
            self._test_document_filename
        )

    def test_uuid_plus_filename_gnerator(self):
        self._test_document_type.filename_generator_backend = UUIDPlusOriginalFilename.name
        self._test_document_type.save()
        self._upload_test_document()
        self.assertTrue(
            str(self._test_document.file_latest.file).endswith(
                self._test_document.file_latest.filename
            )
        )
        self.assertFalse(
            str(self._test_document.file_latest.file).startswith(
                self._test_document.file_latest.filename
            )
        )


class DocumentTypeModelTestCase(GenericDocumentTestCase):
    auto_upload_test_document = False

    def test_method_get_absolute_url(self):
        self.assertTrue(
            self._test_document_type.get_absolute_url()
        )


class DocumentTypeRetentionPoliciesTestCase(GenericDocumentTestCase):
    auto_upload_test_document = False

    def test_auto_trashing(self):
        """
        Test document type trashing policies. Documents are moved to the
        trash, x amount of time after being uploaded
        """
        self._upload_test_document()

        self._test_document_type.trash_time_period = 1
        # 'microseconds' is not a choice via the model, used here for
        # test convenience.
        self._test_document_type.trash_time_unit = 'microseconds'
        self._test_document_type.save()

        self.assertEqual(Document.valid.count(), 1)
        self.assertEqual(TrashedDocument.objects.count(), 0)

        DocumentType.objects.check_trash_periods()

        self.assertEqual(Document.valid.count(), 0)
        self.assertEqual(TrashedDocument.objects.count(), 1)

    def test_auto_delete(self):
        """
        Test document type deletion policies. Documents are deleted from the
        trash, x amount of time after being trashed
        """
        self._upload_test_document()

        self._test_document_type.delete_time_period = 1
        # 'microseconds' is not a choice via the model, used here for
        # test convenience.
        self._test_document_type.delete_time_unit = 'microseconds'
        self._test_document_type.save()

        self.assertEqual(Document.valid.count(), 1)
        self.assertEqual(TrashedDocument.objects.count(), 0)

        self._test_document.delete()

        self.assertEqual(Document.valid.count(), 0)
        self.assertEqual(TrashedDocument.objects.count(), 1)

        DocumentType.objects.check_delete_periods()

        self.assertEqual(Document.valid.count(), 0)
        self.assertEqual(TrashedDocument.objects.count(), 0)

    def test_document_stub_pruning(self):
        self._create_test_document_stub()

        self._test_document_type.document_stub_expiration_interval = 0
        self._test_document_type.save()

        test_document_stub_count = Document.objects.count()

        DocumentType.objects.document_stubs_delete()

        self.assertEqual(
            Document.objects.count(), test_document_stub_count - 1
        )

    def test_document_stub_pruning_disabled(self):
        self._create_test_document_stub()

        self._test_document_type.document_stub_expiration_interval = 0
        self._test_document_type.document_stub_pruning_enabled = False
        self._test_document_type.save()

        test_document_stub_count = Document.objects.count()

        DocumentType.objects.document_stubs_delete()

        self.assertEqual(
            Document.objects.count(), test_document_stub_count
        )

    def test_document_stub_pruning_long_interval(self):
        self._create_test_document_stub()

        self._test_document_type.document_stub_expiration_interval = 3660
        self._test_document_type.save()

        test_document_stub_count = Document.objects.count()

        DocumentType.objects.document_stubs_delete()

        self.assertEqual(
            Document.objects.count(), test_document_stub_count
        )
