import importlib
import logging
from pathlib import Path
import shutil

from django.core.files.base import ContentFile

from mayan.apps.common.tests.literals import (
    TEST_COMPRESSED_FILE_CONTENTS, TEST_FILE_CONTENTS_1, TEST_FILE3_PATH,
    TEST_FILENAME1, TEST_FILENAME3
)
from mayan.apps.documents.literals import STORAGE_NAME_DOCUMENT_FILES
from mayan.apps.permissions.tests.mixins import PermissionTestMixin
from mayan.apps.smart_settings.classes import SettingNamespace

from ..classes import DefinedStorage
from ..compressed_files import Archive
from ..models import DownloadFile, SharedUploadedFile
from ..utils import mkdtemp

from .literals import (
    TEST_DOWNLOAD_FILE_CONTENT_FILE_NAME, TEST_SHARED_UPLOADED_FILE_FILENAME
)


class ArchiveClassTestCaseMixin:
    archive_path = None
    cls = None
    filename = TEST_FILENAME3
    file_path = TEST_FILE3_PATH
    members_list = TEST_COMPRESSED_FILE_CONTENTS
    member_name = TEST_FILENAME1
    member_contents = TEST_FILE_CONTENTS_1

    def test_add_file(self):
        archive = self.cls()
        archive.create()
        with open(file=self.file_path, mode='rb') as file_object:
            archive.add_file(file_object=file_object, filename=self.filename)
            self.assertEqual(
                archive.members(), [self.filename]
            )

    def test_open(self):
        with open(file=self.archive_path, mode='rb') as file_object:
            archive = Archive.open(file_object=file_object)
            self.assertTrue(
                isinstance(archive, self.cls)
            )

    def test_members(self):
        with open(file=self.archive_path, mode='rb') as file_object:
            archive = Archive.open(file_object=file_object)
            self.assertEqual(
                archive.members(), self.members_list
            )

    def test_member_contents(self):
        with open(file=self.archive_path, mode='rb') as file_object:
            archive = Archive.open(file_object=file_object)
            self.assertEqual(
                archive.member_contents(filename=self.member_name),
                self.member_contents
            )

    def test_open_member(self):
        with open(file=self.archive_path, mode='rb') as file_object:
            archive = Archive.open(file_object=file_object)
            file_object = archive.open_member(filename=self.member_name)
            self.assertEqual(
                file_object.read(), self.member_contents
            )


class DownloadFileAPIViewTestMixin:
    def _request_test_download_file_delete_api_view(self):
        return self.delete(
            viewname='rest_api:download_file-detail',
            kwargs={'download_file_id': self._test_download_file.pk}
        )

    def _request_test_download_file_detail_api_view(self):
        return self.get(
            viewname='rest_api:download_file-detail',
            kwargs={'download_file_id': self._test_download_file.pk}
        )

    def _request_test_download_file_download_api_view(self):
        return self.get(
            viewname='rest_api:download_file-download',
            kwargs={'download_file_id': self._test_download_file.pk}
        )

    def _request_test_download_file_list_api_view(self):
        return self.get(viewname='rest_api:download_file-list')


class DownloadFileTestMixin(PermissionTestMixin):
    def setUp(self):
        super().setUp()
        self._test_download_file_list = []

    def _create_test_download_file(self, content=None, user=None):
        file_content = None

        test_download_file_count = len(
            self._test_download_file_list
        )

        test_download_file_filename = '{}_{}'.format(
            TEST_DOWNLOAD_FILE_CONTENT_FILE_NAME,
            test_download_file_count
        )

        if content:
            file_content = ContentFile(
                content=content, name=test_download_file_filename
            )

        self._test_download_file = DownloadFile.objects.create(
            file=file_content, user=user or self._test_case_user
        )

        self._test_download_file_list.append(self._test_download_file)


class DownloadFileViewTestMixin:
    def _request_test_download_file_delete_view(self):
        return self.post(
            viewname='storage:download_file_delete', kwargs={
                'download_file_id': self._test_download_file.pk
            }
        )

    def _request_test_download_file_download_view(self):
        return self.get(
            viewname='storage:download_file_download', kwargs={
                'download_file_id': self._test_download_file.pk
            }
        )

    def _request_test_download_file_list_view(self):
        return self.get(viewname='storage:download_file_list')


class StorageProcessorTestMixin:
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.defined_storage = DefinedStorage.get(
            name=STORAGE_NAME_DOCUMENT_FILES
        )
        cls.document_storage_kwargs = cls.defined_storage.kwargs

    def setUp(self):
        super().setUp()
        self.temporary_directory = mkdtemp()
        self.path_temporary_directory = Path(self.temporary_directory)
        self.path_test_file = self.path_temporary_directory / 'test_file.txt'

    def tearDown(self):
        super().tearDown()
        shutil.rmtree(path=self.temporary_directory, ignore_errors=True)
        self.defined_storage.kwargs = self.document_storage_kwargs


class SharedUploadedFileTestMixin:
    def setUp(self):
        super().setUp()
        self._test_shared_uploaded_file_list = []

    def _create_test_shared_uploaded_file(self, content=None):
        file_content = None

        test_shared_uploaded_file_count = len(
            self._test_shared_uploaded_file_list
        )
        test_shared_uploaded_file_filename = '{}_{}'.format(
            TEST_SHARED_UPLOADED_FILE_FILENAME,
            test_shared_uploaded_file_count
        )

        if content:
            file_content = ContentFile(
                content=content, name=test_shared_uploaded_file_filename
            )

        self._test_shared_uploaded_file = SharedUploadedFile.objects.create(
            file=file_content, filename=test_shared_uploaded_file_filename
        )
        self._test_shared_uploaded_file_list.append(
            self._test_shared_uploaded_file
        )


class StorageSettingTestMixin:
    def _test_storage_setting_with_invalid_value(
        self, setting, storage_module, storage_name
    ):
        old_value = setting.value
        SettingNamespace.invalidate_cache_all()

        self._set_environment_variable(
            name='MAYAN_{}'.format(
                setting.global_name
            ), value='invalid_value'
        )
        self.test_case_silenced_logger_new_level = logging.FATAL + 10
        self._silence_logger(name='mayan.apps.storage.classes')

        with self.assertRaises(expected_exception=TypeError) as assertion:
            importlib.reload(storage_module)
            DefinedStorage.get(
                name=storage_name
            ).get_storage_instance()

        setting.set(value=old_value)
        importlib.reload(storage_module)

        return assertion
