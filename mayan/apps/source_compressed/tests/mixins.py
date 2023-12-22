from mayan.apps.documents.tests.literals import TEST_FILE_SMALL_PATH

from mayan.apps.sources.tests.mixins.base_mixins import SourceTestMixin

from .literals import TEST_SOURCE_BACKEND_PATH_COMPRESSED


class CompressedSourceTestMixin(SourceTestMixin):
    _test_source_backend_path = TEST_SOURCE_BACKEND_PATH_COMPRESSED
    _test_source_file_path = TEST_FILE_SMALL_PATH
