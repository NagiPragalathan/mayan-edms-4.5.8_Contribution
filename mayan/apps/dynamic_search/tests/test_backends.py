from unittest import mock, skip

from mayan.apps.documents.tests.mixins.document_mixins import DocumentTestMixin
from mayan.apps.tags.tests.mixins import TagTestMixin
from mayan.apps.testing.tests.base import BaseTestCase

from ..exceptions import DynamicSearchBackendException
from ..search_query_types import QueryTypeExact

from .mixins.base import SearchTestMixin, TestSearchObjectSimpleTestMixin
from .mixins.backend_mixins import BackendSearchTestMixin
from .mixins.backend_search_field_mixins import BackendSearchFieldTestCaseMixin
from .mixins.backend_query_type_mixins import BackendFieldTypeQueryTypeTestCaseMixin


class DjangoSearchBackendSearchFieldTestCase(
    BackendSearchFieldTestCaseMixin, BaseTestCase
):
    _test_search_backend_path = 'mayan.apps.dynamic_search.backends.django.DjangoSearchBackend'


class DjangoSearchBackendFieldTypeQueryTypeTestCase(
    BackendFieldTypeQueryTypeTestCaseMixin, BaseTestCase
):
    _test_search_backend_path = 'mayan.apps.dynamic_search.backends.django.DjangoSearchBackend'

    @skip(reason='Backend does not support the feature.')
    def test_search_field_type_char_search_exact_accent(self):
        """
        This backend does not require indexing which is required
        for this feature to work.
        """

    @skip(reason='Backend does not support the feature.')
    def test_search_field_type_char_search_fuzzy(self):
        """
        This query type is emulated and does not return the same results
        as backends support this natively.
        """

    @skip(reason='Backend does not support the feature.')
    def test_search_field_type_text_search_fuzzy(self):
        """
        This query type is emulated and does not return the same results
        as backends support this natively.
        """


@skip(reason='Skip until a Mock ElasticSearch server class is added.')
class ElasticSearchBackendIndexingTestCase(
    BackendSearchTestMixin, TestSearchObjectSimpleTestMixin, SearchTestMixin,
    BaseTestCase
):
    _test_search_backend_path = 'mayan.apps.dynamic_search.backends.elasticsearch.ElasticSearchBackend'

    def test_search_without_indexes(self):
        self._test_search_backend.tear_down()

        with self.assertRaises(expected_exception=DynamicSearchBackendException):
            self._do_backend_search(
                field_name='char',
                query_type=QueryTypeExact,
                value=self._test_object.char,
                _skip_refresh=True,
            )


@skip(reason='Skip until a Mock ElasticSearch server class is added.')
class ElasticSearchBackendSearchFieldTestCase(
    BackendSearchFieldTestCaseMixin, BaseTestCase
):
    _test_search_backend_path = 'mayan.apps.dynamic_search.backends.elasticsearch.ElasticSearchBackend'


@skip(reason='Skip until a Mock ElasticSearch server class is added.')
class ElasticSearchBackendFieldTypeQueryTypeTestCase(
    BackendFieldTypeQueryTypeTestCaseMixin, BaseTestCase
):
    _test_search_backend_path = 'mayan.apps.dynamic_search.backends.elasticsearch.ElasticSearchBackend'


class WhooshSearchBackendSearchFieldTestCase(
    BackendSearchFieldTestCaseMixin, BaseTestCase
):
    _test_search_backend_path = 'mayan.apps.dynamic_search.backends.whoosh.WhooshSearchBackend'


class WhooshSearchBackendFieldTypeQueryTypeTestCase(
    BackendFieldTypeQueryTypeTestCaseMixin, BaseTestCase
):
    _test_search_backend_path = 'mayan.apps.dynamic_search.backends.whoosh.WhooshSearchBackend'


class WhooshSearchBackendSpecificTestCase(
    BackendSearchTestMixin, TestSearchObjectSimpleTestMixin, SearchTestMixin,
    BaseTestCase
):
    _test_search_backend_path = 'mayan.apps.dynamic_search.backends.whoosh.WhooshSearchBackend'

    def test_whoosh_datetime_search_raw_parsed_date_human_today(self):
        id_list = self._do_backend_search(
            field_name='datetime',
            is_raw_value=True,
            query_type=QueryTypeExact,
            value='today'
        )

        self.assertEqual(len(id_list), 1)
        self.assertTrue(self._test_object.id in id_list)

    def test_whoosh_datetime_search_raw_parsed_date_human_range(self):
        id_list = self._do_backend_search(
            field_name='datetime',
            is_raw_value=True,
            query_type=QueryTypeExact,
            value='[\'last tuesday\' to \'next friday\']'
        )

        self.assertEqual(len(id_list), 1)
        self.assertTrue(self._test_object.id in id_list)

    def test_whoosh_datetime_search_raw_parsed_date_numeric_range(self):
        id_list = self._do_backend_search(
            field_name='datetime',
            is_raw_value=True,
            query_type=QueryTypeExact,
            value='[\'{}\' to \'{}\']'.format(
                self._test_object.datetime.year - 1,
                self._test_object.datetime.year + 1
            )
        )

        self.assertEqual(len(id_list), 1)
        self.assertTrue(self._test_object.id in id_list)

    def test_whoosh_integer_search_raw_parsed_numeric_range(self):
        id_list = self._do_backend_search(
            field_name='integer',
            is_raw_value=True,
            query_type=QueryTypeExact,
            value='[\'{}\' to \'{}\']'.format(
                self._test_object.integer - 1,
                self._test_object.integer + 1
            )
        )

        self.assertEqual(len(id_list), 1)
        self.assertTrue(self._test_object.id in id_list)


class SearchUpdatePropagationTestCase(
    DocumentTestMixin, SearchTestMixin, TagTestMixin, BaseTestCase
):
    _test_search_backend_path = 'mayan.apps.dynamic_search.tests.backends.DummySearchBackend'
    auto_upload_test_document = False

    def setUp(self):
        super().setUp()

        self._create_test_document_stub()
        self._create_test_document_stub()
        self._create_test_document_stub()
        self._create_test_tag()

    @mock.patch(target='mayan.apps.dynamic_search.tests.backends.DummySearchBackend.index_instance')
    def test_m2m_add_propagation(self, mocked_index_instance):
        self._test_tag._attach_to(
            document=self._test_documents[0]
        )
        self.assertEqual(mocked_index_instance.call_count, 2)
        self.assertEqual(
            mocked_index_instance.call_args_list[0].kwargs['instance'],
            self._test_documents[0]
        )
        self.assertEqual(
            mocked_index_instance.call_args_list[1].kwargs['instance'],
            self._test_tag_list[0]
        )

        mocked_index_instance.reset_mock()

        self._test_tag._attach_to(
            document=self._test_documents[1]
        )
        self.assertEqual(mocked_index_instance.call_count, 2)
        self.assertEqual(
            mocked_index_instance.call_args_list[0].kwargs['instance'],
            self._test_documents[1]
        )
        self.assertEqual(
            mocked_index_instance.call_args_list[1].kwargs['instance'],
            self._test_tag_list[0]
        )

        mocked_index_instance.reset_mock()

        self._test_tag._attach_to(
            document=self._test_documents[2]
        )
        self.assertEqual(mocked_index_instance.call_count, 2)
        self.assertEqual(
            mocked_index_instance.call_args_list[0].kwargs['instance'],
            self._test_documents[2]
        )
        self.assertEqual(
            mocked_index_instance.call_args_list[1].kwargs['instance'],
            self._test_tag_list[0]
        )

        mocked_index_instance.reset_mock()

        self._test_tag.label = 'edited'
        self._test_tag.save()
        self.assertEqual(mocked_index_instance.call_count, 4)
        self.assertEqual(
            mocked_index_instance.call_args_list[0].kwargs['instance'],
            self._test_documents[0]
        )
        self.assertEqual(
            mocked_index_instance.call_args_list[1].kwargs['instance'],
            self._test_documents[1]
        )
        self.assertEqual(
            mocked_index_instance.call_args_list[2].kwargs['instance'],
            self._test_documents[2]
        )
        self.assertEqual(
            mocked_index_instance.call_args_list[3].kwargs['instance'],
            self._test_tag_list[0]
        )

        mocked_index_instance.reset_mock()

        self._test_tag._remove_from(
            document=self._test_documents[0]
        )
        self.assertEqual(mocked_index_instance.call_count, 2)
        self.assertEqual(
            mocked_index_instance.call_args_list[0].kwargs['instance'],
            self._test_documents[0]
        )
        self.assertEqual(
            mocked_index_instance.call_args_list[1].kwargs['instance'],
            self._test_tag_list[0]
        )
