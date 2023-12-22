from ...literals import QUERY_PARAMETER_ANY_FIELD
from ...search_query_types import (
    QueryTypeExact, QueryTypeFuzzy, QueryTypeGreaterThan,
    QueryTypeGreaterThanOrEqual, QueryTypeLessThan, QueryTypeLessThanOrEqual,
    QueryTypePartial, QueryTypeRange, QueryTypeRangeExclusive,
    QueryTypeRegularExpression
)

from ..literals import TEST_OBJECT_INTEGER_VALUE

from .backend_mixins import BackendSearchTestMixin
from .base import SearchTestMixin, TestSearchObjectSimpleTestMixin


class BackendFieldTypeQueryTypeAnyTestCaseMixin:
    def test_search_field_type_any_search_empty_non_quoted(self):
        id_list = self._do_backend_search(
            field_name=QUERY_PARAMETER_ANY_FIELD,
            query_type=QueryTypeExact,
            value=''
        )

        self.assertEqual(
            len(id_list), 0
        )

    def test_search_field_type_any_search_empty_quoted(self):
        id_list = self._do_backend_search(
            field_name=QUERY_PARAMETER_ANY_FIELD,
            is_quoted_value=True,
            query_type=QueryTypeExact,
            value=''
        )

        self.assertEqual(
            len(id_list), 0
        )

    def test_search_field_type_any_search_exact(self):
        id_list = self._do_backend_search(
            field_name=QUERY_PARAMETER_ANY_FIELD,
            query_type=QueryTypeExact,
            value=self._test_object.char
        )

        self.assertEqual(
            len(id_list), 1
        )
        self.assertTrue(self._test_object.id in id_list)

    def test_search_field_type_any_search_exact_case_insensitive(self):
        self._test_object.char = self._test_object.char.upper()
        self._test_object.save()

        id_list = self._do_backend_search(
            field_name=QUERY_PARAMETER_ANY_FIELD,
            query_type=QueryTypeExact,
            value=self._test_object.char.lower()
        )

        self.assertEqual(
            len(id_list), 1
        )
        self.assertTrue(self._test_object.id in id_list)

        self._test_object.char = self._test_object.char.lower()
        self._test_object.save()

        id_list = self._do_backend_search(
            field_name=QUERY_PARAMETER_ANY_FIELD,
            query_type=QueryTypeExact,
            value=self._test_object.char.upper()
        )

        self.assertEqual(
            len(id_list), 1
        )
        self.assertTrue(self._test_object.id in id_list)

    def test_search_field_type_any_search_partial(self):
        parts = self._test_object.char.split(' ')

        id_list = self._do_backend_search(
            field_name=QUERY_PARAMETER_ANY_FIELD,
            query_type=QueryTypePartial,
            value=parts[0][:-1]
        )

        self.assertEqual(
            len(id_list), 1
        )
        self.assertTrue(self._test_object.id in id_list)

        id_list = self._do_backend_search(
            field_name=QUERY_PARAMETER_ANY_FIELD,
            query_type=QueryTypePartial,
            value=parts[0][1:]
        )

        self.assertEqual(
            len(id_list), 1
        )
        self.assertTrue(self._test_object.id in id_list)

        id_list = self._do_backend_search(
            field_name=QUERY_PARAMETER_ANY_FIELD,
            query_type=QueryTypePartial,
            value=parts[0].upper()[:-1]
        )

        self.assertEqual(
            len(id_list), 1
        )
        self.assertTrue(self._test_object.id in id_list)

        id_list = self._do_backend_search(
            field_name=QUERY_PARAMETER_ANY_FIELD,
            query_type=QueryTypePartial,
            value=parts[0].upper()[1:]
        )

        self.assertEqual(
            len(id_list), 1
        )
        self.assertTrue(self._test_object.id in id_list)

        id_list = self._do_backend_search(
            field_name=QUERY_PARAMETER_ANY_FIELD,
            is_quoted_value=True,
            query_type=QueryTypePartial,
            value=' '.join((parts[0], parts[1]))
        )

        self.assertEqual(
            len(id_list), 1
        )
        self.assertTrue(self._test_object.id in id_list)

        id_list = self._do_backend_search(
            field_name=QUERY_PARAMETER_ANY_FIELD,
            is_quoted_value=True,
            query_type=QueryTypePartial,
            value=' '.join((parts[1], parts[0]))
        )

        self.assertEqual(
            len(id_list), 0
        )

        id_list = self._do_backend_search(
            field_name=QUERY_PARAMETER_ANY_FIELD,
            is_quoted_value=True,
            query_type=QueryTypePartial,
            value=' '.join((parts[0], parts[2]))
        )

        self.assertEqual(
            len(id_list), 0
        )

        id_list = self._do_backend_search(
            field_name=QUERY_PARAMETER_ANY_FIELD,
            query_type=QueryTypePartial,
            value=self._test_object.email[1:-1]
        )

        self.assertEqual(
            len(id_list), 1
        )
        self.assertTrue(self._test_object.id in id_list)

        id_list = self._do_backend_search(
            field_name=QUERY_PARAMETER_ANY_FIELD,
            query_type=QueryTypePartial,
            value=str(self._test_object.uuid).split('-')[0]
        )

        self.assertEqual(
            len(id_list), 1
        )
        self.assertTrue(self._test_object.id in id_list)

    def test_search_field_type_any_search_exact_invalid(self):
        id_list = self._do_backend_search(
            field_name=QUERY_PARAMETER_ANY_FIELD,
            query_type=QueryTypeExact,
            value=1.1
        )

        self.assertEqual(
            len(id_list), 0
        )

    def test_search_field_type_any_search_partial_invalid(self):
        id_list = self._do_backend_search(
            field_name=QUERY_PARAMETER_ANY_FIELD,
            query_type=QueryTypePartial,
            value='1970-01'
        )

        self.assertEqual(
            len(id_list), 0
        )


class BackendFieldTypeQueryTypeAutoFieldTestCaseMixin:
    def test_search_field_type_autofield_search_empty_non_quoted(self):
        id_list = self._do_backend_search(
            field_name='id',
            query_type=QueryTypeExact,
            value=''
        )

        self.assertEqual(
            len(id_list), 0
        )

    def test_search_field_type_autofield_search_exact(self):
        id_list = self._do_backend_search(
            field_name='id',
            query_type=QueryTypeExact,
            value=self._test_object.id
        )

        self.assertEqual(
            len(id_list), 1
        )
        self.assertTrue(self._test_object.id in id_list)

        id_list = self._do_backend_search(
            field_name='id',
            query_type=QueryTypeExact,
            value=str(self._test_object.id)
        )

        self.assertEqual(
            len(id_list), 1
        )
        self.assertTrue(self._test_object.id in id_list)

    def test_search_field_type_autofield_search_greater_than(self):
        id_list = self._do_backend_search(
            field_name='id',
            query_type=QueryTypeGreaterThan,
            value=self._test_object.id - 1
        )

        self.assertEqual(
            len(id_list), 1
        )
        self.assertTrue(self._test_object.id in id_list)

    def test_search_field_type_autofield_search_greater_than_or_equal(self):
        id_list = self._do_backend_search(
            field_name='id',
            query_type=QueryTypeGreaterThanOrEqual,
            value=self._test_object.id - 1
        )

        self.assertEqual(
            len(id_list), 1
        )
        self.assertTrue(self._test_object.id in id_list)

        id_list = self._do_backend_search(
            field_name='id',
            query_type=QueryTypeGreaterThanOrEqual,
            value=self._test_object.id
        )

        self.assertEqual(
            len(id_list), 1
        )
        self.assertTrue(self._test_object.id in id_list)

    def test_search_field_type_autofield_search_less_than(self):
        id_list = self._do_backend_search(
            field_name='id',
            query_type=QueryTypeLessThan,
            value=self._test_object.id + 1
        )

        self.assertEqual(
            len(id_list), 1
        )
        self.assertTrue(self._test_object.id in id_list)

    def test_search_field_type_autofield_search_less_than_or_equal(self):
        id_list = self._do_backend_search(
            field_name='id',
            query_type=QueryTypeLessThanOrEqual,
            value=self._test_object.id + 1
        )

        self.assertEqual(
            len(id_list), 1
        )
        self.assertTrue(self._test_object.id in id_list)

        id_list = self._do_backend_search(
            field_name='id',
            query_type=QueryTypeLessThanOrEqual,
            value=self._test_object.id
        )

        self.assertEqual(
            len(id_list), 1
        )
        self.assertTrue(self._test_object.id in id_list)

    def test_search_field_type_autofield_search_range(self):
        id_list = self._do_backend_search(
            field_name='id',
            query_type=QueryTypeRange,
            value='{}..{}'.format(
                self._test_object.id - 1, self._test_object.id + 1
            )
        )

        self.assertEqual(
            len(id_list), 1
        )
        self.assertTrue(self._test_object.id in id_list)

        id_list = self._do_backend_search(
            field_name='id',
            query_type=QueryTypeRange,
            value='{}..{}'.format(
                self._test_object.id, self._test_object.id + 1
            )
        )

        self.assertEqual(
            len(id_list), 1
        )
        self.assertTrue(self._test_object.id in id_list)

        id_list = self._do_backend_search(
            field_name='id',
            query_type=QueryTypeRange,
            value='{}..{}'.format(
                self._test_object.id - 1, self._test_object.id
            )
        )

        self.assertEqual(
            len(id_list), 1
        )
        self.assertTrue(self._test_object.id in id_list)

        id_list = self._do_backend_search(
            field_name='id',
            query_type=QueryTypeRange,
            value='{}..{}'.format(
                self._test_object.id, self._test_object.id
            )
        )

        self.assertEqual(
            len(id_list), 1
        )
        self.assertTrue(self._test_object.id in id_list)

    def test_search_field_type_autofield_search_range_exclusive(self):
        id_list = self._do_backend_search(
            field_name='id',
            query_type=QueryTypeRangeExclusive,
            value='{}..{}'.format(
                self._test_object.id - 1, self._test_object.id + 1
            )
        )

        self.assertEqual(
            len(id_list), 1
        )
        self.assertTrue(self._test_object.id in id_list)

        id_list = self._do_backend_search(
            field_name='id',
            query_type=QueryTypeRangeExclusive,
            value='{}..{}'.format(
                self._test_object.id, self._test_object.id + 1
            )
        )

        self.assertEqual(
            len(id_list), 0
        )

        id_list = self._do_backend_search(
            field_name='id',
            query_type=QueryTypeRangeExclusive,
            value='{}..{}'.format(
                self._test_object.id - 1, self._test_object.id
            )
        )

        self.assertEqual(
            len(id_list), 0
        )

        id_list = self._do_backend_search(
            field_name='id',
            query_type=QueryTypeRangeExclusive,
            value='{}..{}'.format(
                self._test_object.id, self._test_object.id
            )
        )

        self.assertEqual(
            len(id_list), 0
        )

    def test_search_field_type_autofield_search_range_exclusive_invalid(self):
        id_list = self._do_backend_search(
            field_name='id',
            query_type=QueryTypeRangeExclusive,
            value='INVALID'
        )

        self.assertEqual(
            len(id_list), 0
        )

        id_list = self._do_backend_search(
            field_name='id',
            query_type=QueryTypeRangeExclusive,
            value=True
        )

        self.assertEqual(
            len(id_list), 0
        )


class BackendFieldTypeQueryTypeBooleanTestCaseMixin:
    def test_search_field_type_boolean_search_empty_non_quoted(self):
        id_list = self._do_backend_search(
            field_name='boolean',
            query_type=QueryTypeExact,
            value=''
        )

        self.assertEqual(
            len(id_list), 0
        )

        self._test_object.boolean = False
        self._test_object.save()

        id_list = self._do_backend_search(
            field_name='boolean',
            query_type=QueryTypeExact,
            value=''
        )

        self.assertEqual(
            len(id_list), 0
        )

    def test_search_field_type_boolean_search_exact(self):
        id_list = self._do_backend_search(
            field_name='boolean',
            query_type=QueryTypeExact,
            value=True
        )

        self.assertEqual(
            len(id_list), 1
        )
        self.assertTrue(self._test_object.id in id_list)

        id_list = self._do_backend_search(
            field_name='boolean',
            query_type=QueryTypeExact,
            value='true'
        )

        self.assertEqual(
            len(id_list), 1
        )
        self.assertTrue(self._test_object.id in id_list)

        id_list = self._do_backend_search(
            field_name='boolean',
            query_type=QueryTypeExact,
            value='TRUE'
        )

        self.assertEqual(
            len(id_list), 1
        )
        self.assertTrue(self._test_object.id in id_list)

        id_list = self._do_backend_search(
            field_name='boolean',
            query_type=QueryTypeExact,
            value=False
        )

        self.assertEqual(
            len(id_list), 0
        )

        id_list = self._do_backend_search(
            field_name='boolean',
            query_type=QueryTypeExact,
            value='false'
        )

        self.assertEqual(
            len(id_list), 0
        )

        id_list = self._do_backend_search(
            field_name='boolean',
            query_type=QueryTypeExact,
            value='FALSE'
        )

        self.assertEqual(
            len(id_list), 0
        )

        self._test_object.boolean = False
        self._test_object.save()

        id_list = self._do_backend_search(
            field_name='boolean',
            query_type=QueryTypeExact,
            value='FALSE'
        )

        self.assertEqual(
            len(id_list), 1
        )
        self.assertTrue(self._test_object.id in id_list)


class BackendFieldTypeQueryTypeCharTestCaseMixin:
    def test_search_field_type_char_search_empty_non_quoted(self):
        id_list = self._do_backend_search(
            field_name='char',
            query_type=QueryTypeExact,
            value=''
        )

        self.assertEqual(
            len(id_list), 0
        )

        self._test_object.char = ''
        self._test_object.save()

        id_list = self._do_backend_search(
            field_name='char',
            query_type=QueryTypeExact,
            value=''
        )

        self.assertEqual(
            len(id_list), 0
        )

    def test_search_field_type_char_search_empty_quoted(self):
        id_list = self._do_backend_search(
            field_name='char',
            is_quoted_value=True,
            query_type=QueryTypeExact,
            value=''
        )

        self.assertEqual(
            len(id_list), 0
        )

        self._test_object.char = ''
        self._test_object.save()

        id_list = self._do_backend_search(
            field_name='char',
            is_quoted_value=True,
            query_type=QueryTypeExact,
            value=''
        )

        self.assertEqual(
            len(id_list), 1
        )
        self.assertTrue(self._test_object.id in id_list)

    def test_search_field_type_char_search_exact_accent(self):
        self._test_object.char = 'café'
        self._test_object.save()

        id_list = self._do_backend_search(
            field_name='char',
            query_type=QueryTypeExact,
            value='cafe'
        )

        self.assertEqual(
            len(id_list), 1
        )
        self.assertTrue(self._test_object.id in id_list)

    def test_search_field_type_char_search_exact(self):
        parts = self._test_object.char.split(' ')

        id_list = self._do_backend_search(
            field_name='char',
            query_type=QueryTypeExact,
            value=parts[0]
        )

        self.assertEqual(
            len(id_list), 1
        )
        self.assertTrue(self._test_object.id in id_list)

        id_list = self._do_backend_search(
            field_name='char',
            query_type=QueryTypeExact,
            value=''.join((parts[0], parts[1]))
        )

        self.assertEqual(
            len(id_list), 0
        )

        id_list = self._do_backend_search(
            field_name='char',
            query_type=QueryTypeExact,
            value=parts[0][1:]
        )

        self.assertEqual(
            len(id_list), 0
        )

        id_list = self._do_backend_search(
            field_name='char',
            is_quoted_value=True,
            query_type=QueryTypeExact,
            value=self._test_object.char
        )

        self.assertEqual(
            len(id_list), 1
        )
        self.assertTrue(self._test_object.id in id_list)

        id_list = self._do_backend_search(
            field_name='char',
            is_quoted_value=True,
            query_type=QueryTypeExact,
            value=' '.join((parts[2], parts[1], parts[0]))
        )

        self.assertEqual(
            len(id_list), 0
        )

    def test_search_field_type_char_search_fuzzy(self):
        id_list = self._do_backend_search(
            field_name='char',
            query_type=QueryTypeFuzzy,
            value='chra'
        )

        self.assertEqual(
            len(id_list), 1
        )
        self.assertTrue(self._test_object.id in id_list)

        id_list = self._do_backend_search(
            field_name='char',
            is_quoted_value=True,
            query_type=QueryTypeFuzzy,
            value='test chra'
        )

        self.assertEqual(
            len(id_list), 0
        )

    def test_search_field_type_char_search_partial(self):
        parts = self._test_object.char.split(' ')

        id_list = self._do_backend_search(
            field_name='char',
            query_type=QueryTypePartial,
            value=parts[0][:-1]
        )

        self.assertEqual(
            len(id_list), 1
        )
        self.assertTrue(self._test_object.id in id_list)

        id_list = self._do_backend_search(
            field_name='char',
            query_type=QueryTypePartial,
            value=parts[0][1:]
        )

        self.assertEqual(
            len(id_list), 1
        )
        self.assertTrue(self._test_object.id in id_list)

        id_list = self._do_backend_search(
            field_name='char',
            query_type=QueryTypePartial,
            value=parts[0].upper()[:-1]
        )

        self.assertEqual(
            len(id_list), 1
        )
        self.assertTrue(self._test_object.id in id_list)

        id_list = self._do_backend_search(
            field_name='char',
            query_type=QueryTypePartial,
            value=parts[0].upper()[1:]
        )

        self.assertEqual(
            len(id_list), 1
        )
        self.assertTrue(self._test_object.id in id_list)

        id_list = self._do_backend_search(
            field_name='char',
            is_quoted_value=True,
            query_type=QueryTypePartial,
            value=' '.join((parts[0], parts[1]))
        )

        self.assertEqual(
            len(id_list), 1
        )
        self.assertTrue(self._test_object.id in id_list)

        id_list = self._do_backend_search(
            field_name='char',
            is_quoted_value=True,
            query_type=QueryTypePartial,
            value=' '.join((parts[1], parts[0]))
        )

        self.assertEqual(
            len(id_list), 0
        )

        id_list = self._do_backend_search(
            field_name='char',
            is_quoted_value=True,
            query_type=QueryTypePartial,
            value=' '.join((parts[0], parts[2]))
        )

        self.assertEqual(
            len(id_list), 0
        )

    def test_search_field_type_char_search_regular_expression(self):
        id_list = self._do_backend_search(
            field_name='char',
            query_type=QueryTypeRegularExpression,
            value='c.*r'
        )

        self.assertEqual(
            len(id_list), 1
        )
        self.assertTrue(self._test_object.id in id_list)

        id_list = self._do_backend_search(
            field_name='char',
            query_type=QueryTypeRegularExpression,
            value='(test|INVALID)'
        )

        self.assertEqual(
            len(id_list), 1
        )
        self.assertTrue(self._test_object.id in id_list)

    def test_search_field_type_char_search_invalid(self):
        id_list = self._do_backend_search(
            field_name='char',
            query_type=QueryTypeExact,
            value=99
        )

        self.assertEqual(
            len(id_list), 0
        )


class BackendFieldTypeQueryTypeDateTimeTestCaseMixin:
    def test_search_field_type_datetime_search_empty_non_quoted(self):
        id_list = self._do_backend_search(
            field_name='datetime',
            query_type=QueryTypeExact,
            value=''
        )

        self.assertEqual(
            len(id_list), 0
        )

        self._test_object.datetime = None
        self._test_object.save()

        id_list = self._do_backend_search(
            field_name='datetime',
            query_type=QueryTypeExact,
            value=''
        )

        self.assertEqual(
            len(id_list), 0
        )

    def test_search_field_type_datetime_search_empty_quoted(self):
        id_list = self._do_backend_search(
            field_name='datetime',
            is_quoted_value=True,
            query_type=QueryTypeExact,
            value=''
        )

        self.assertEqual(
            len(id_list), 0
        )

        self._test_object.datetime = None
        self._test_object.save()

        id_list = self._do_backend_search(
            field_name='datetime',
            is_quoted_value=True,
            query_type=QueryTypeExact,
            value=''
        )

        self.assertEqual(
            len(id_list), 0
        )

    def test_search_field_type_datetime_search_exact(self):
        id_list = self._do_backend_search(
            field_name='datetime',
            query_type=QueryTypeExact,
            value='{year}-{month}-{day}T{hour}:{minute}:{second}'.format(
                year=self._test_object.datetime.year,
                month=self._test_object.datetime.month,
                day=self._test_object.datetime.day,
                hour=self._test_object.datetime.hour,
                minute=self._test_object.datetime.minute,
                second=self._test_object.datetime.second
            )
        )

        self.assertEqual(
            len(id_list), 1
        )
        self.assertTrue(self._test_object.id in id_list)

    def test_search_field_type_datetime_search_greater_than(self):
        id_list = self._do_backend_search(
            field_name='datetime',
            query_type=QueryTypeGreaterThan, value='{year}-{month}'.format(
                year=self._test_object.datetime.year - 1,
                month=self._test_object.datetime.month
            )
        )

        self.assertEqual(
            len(id_list), 1
        )
        self.assertTrue(self._test_object.id in id_list)

    def test_search_field_type_datetime_search_greater_than_humanized_quoted(self):
        id_list = self._do_backend_search(
            field_name='datetime',
            is_quoted_value=True,
            query_type=QueryTypeGreaterThan,
            value='last month'
        )

        self.assertEqual(
            len(id_list), 1
        )
        self.assertTrue(self._test_object.id in id_list)

    def test_search_field_type_datetime_search_greater_than_humanized_non_quoted(self):
        id_list = self._do_backend_search(
            field_name='datetime',
            query_type=QueryTypeGreaterThan,
            value='last month'
        )

        self.assertEqual(
            len(id_list), 1
        )
        self.assertTrue(self._test_object.id in id_list)

    def test_search_field_type_datetime_search_greater_than_or_equal(self):
        id_list = self._do_backend_search(
            field_name='datetime',
            query_type=QueryTypeGreaterThanOrEqual,
            value='{year}-{month}'.format(
                year=self._test_object.datetime.year - 1,
                month=self._test_object.datetime.month
            )
        )

        self.assertEqual(
            len(id_list), 1
        )
        self.assertTrue(self._test_object.id in id_list)

    def test_search_field_type_datetime_search_less_than(self):
        id_list = self._do_backend_search(
            field_name='datetime',
            query_type=QueryTypeLessThan, value='{year}-{month}'.format(
                year=self._test_object.datetime.year + 1,
                month=self._test_object.datetime.month
            )
        )

        self.assertEqual(
            len(id_list), 1
        )
        self.assertTrue(self._test_object.id in id_list)

    def test_search_field_type_datetime_search_less_than_humanized(self):
        id_list = self._do_backend_search(
            field_name='datetime',
            query_type=QueryTypeLessThan, value='tomorrow'
        )

        self.assertEqual(
            len(id_list), 1
        )
        self.assertTrue(self._test_object.id in id_list)

    def test_search_field_type_datetime_search_less_than_or_equal(self):
        id_list = self._do_backend_search(
            field_name='datetime',
            query_type=QueryTypeLessThanOrEqual,
            value='{year}-{month}'.format(
                year=self._test_object.datetime.year + 1,
                month=self._test_object.datetime.month
            )
        )

        self.assertEqual(
            len(id_list), 1
        )
        self.assertTrue(self._test_object.id in id_list)

    def test_search_field_type_datetime_search_range(self):
        id_list = self._do_backend_search(
            field_name='datetime',
            query_type=QueryTypeRange,
            value='{year_low}-{month_low}..{year_high}-{month_high}'.format(
                year_low=self._test_object.datetime.year - 1,
                month_low=self._test_object.datetime.month,
                year_high=self._test_object.datetime.year + 1,
                month_high=self._test_object.datetime.month
            )
        )

        self.assertEqual(
            len(id_list), 1
        )
        self.assertTrue(self._test_object.id in id_list)

    def test_search_field_type_datetime_search_range_humanized(self):
        id_list = self._do_backend_search(
            field_name='datetime',
            is_quoted_value=True,
            query_type=QueryTypeRange,
            value='last year..tomorrow'
        )

        self.assertEqual(
            len(id_list), 1
        )
        self.assertTrue(self._test_object.id in id_list)

        id_list = self._do_backend_search(
            field_name='datetime',
            is_quoted_value=True,
            query_type=QueryTypeRange,
            value='yesterday..in two months'
        )

        self.assertEqual(
            len(id_list), 1
        )
        self.assertTrue(self._test_object.id in id_list)

    def test_search_field_type_datetime_search_range_humanized_non_quoted(self):
        id_list = self._do_backend_search(
            field_name='datetime',
            query_type=QueryTypeRange,
            value='last year..tomorrow'
        )

        self.assertEqual(
            len(id_list), 1
        )
        self.assertTrue(self._test_object.id in id_list)

    def test_search_field_type_datetime_search_range_exclusive(self):
        id_list = self._do_backend_search(
            field_name='datetime',
            query_type=QueryTypeRangeExclusive,
            value='{year_low}-{month_low}..{year_high}-{month_high}'.format(
                year_low=self._test_object.datetime.year - 1,
                month_low=self._test_object.datetime.month,
                year_high=self._test_object.datetime.year + 1,
                month_high=self._test_object.datetime.month
            )
        )

        self.assertEqual(
            len(id_list), 1
        )
        self.assertTrue(self._test_object.id in id_list)

    def test_search_field_type_datetime_search_range_invalid(self):
        id_list = self._do_backend_search(
            field_name='datetime',
            query_type=QueryTypeRangeExclusive,
            value=11111
        )

        self.assertEqual(
            len(id_list), 0
        )

        id_list = self._do_backend_search(
            field_name='datetime',
            query_type=QueryTypeRangeExclusive,
            value='invalid'
        )

        self.assertEqual(
            len(id_list), 0
        )

        id_list = self._do_backend_search(
            field_name='datetime',
            query_type=QueryTypeRangeExclusive,
            value=True
        )

        self.assertEqual(
            len(id_list), 0
        )


class BackendFieldTypeQueryTypeEmailTestCaseMixin:
    def test_search_field_type_email_search_exact_empty_non_quoted(self):
        id_list = self._do_backend_search(
            field_name='email',
            query_type=QueryTypeExact,
            value=''
        )

        self.assertEqual(
            len(id_list), 0
        )

        self._test_object.email = ''
        self._test_object.save()

        id_list = self._do_backend_search(
            field_name='email',
            query_type=QueryTypeExact,
            value=''
        )

        self.assertEqual(
            len(id_list), 0
        )

    def test_search_field_type_email_search_exact_empty_quoted(self):
        id_list = self._do_backend_search(
            field_name='email',
            is_quoted_value=True,
            query_type=QueryTypeExact,
            value=''
        )

        self.assertEqual(
            len(id_list), 0
        )

        self._test_object.email = ''
        self._test_object.save()

        id_list = self._do_backend_search(
            field_name='email',
            is_quoted_value=True,
            query_type=QueryTypeExact,
            value=''
        )

        self.assertEqual(
            len(id_list), 1
        )
        self.assertTrue(self._test_object.id in id_list)

    def test_search_field_type_email_search_exact(self):
        id_list = self._do_backend_search(
            field_name='email',
            query_type=QueryTypeExact,
            value=self._test_object.email
        )

        self.assertEqual(
            len(id_list), 1
        )
        self.assertTrue(self._test_object.id in id_list)

    def test_search_field_type_email_search_partial(self):
        id_list = self._do_backend_search(
            field_name='email',
            query_type=QueryTypePartial,
            value='user'
        )

        self.assertEqual(
            len(id_list), 1
        )
        self.assertTrue(self._test_object.id in id_list)

        id_list = self._do_backend_search(
            field_name='email',
            query_type=QueryTypePartial,
            value='user@'
        )

        self.assertEqual(
            len(id_list), 1
        )
        self.assertTrue(self._test_object.id in id_list)

        id_list = self._do_backend_search(
            field_name='email',
            query_type=QueryTypePartial,
            value='example.org'
        )

        self.assertEqual(
            len(id_list), 1
        )
        self.assertTrue(self._test_object.id in id_list)

        id_list = self._do_backend_search(
            field_name='email',
            query_type=QueryTypePartial,
            value=self._test_object.email[1:-1]
        )

        self.assertEqual(
            len(id_list), 1
        )
        self.assertTrue(self._test_object.id in id_list)

    def test_search_field_type_email_search_exact_invalid(self):
        id_list = self._do_backend_search(
            field_name='email',
            query_type=QueryTypeExact,
            value=99
        )

        self.assertEqual(
            len(id_list), 0
        )

        id_list = self._do_backend_search(
            field_name='email',
            query_type=QueryTypeExact,
            value=True
        )

        self.assertEqual(
            len(id_list), 0
        )


class BackendFieldTypeQueryTypeIntegerTestCaseMixin:
    def test_search_field_type_integer_null_search_exact_empty_non_quoted(self):
        self._test_object_integer_set = False

        id_list = self._do_backend_search(
            field_name='integer',
            query_type=QueryTypeExact,
            value=''
        )

        self.assertEqual(
            len(id_list), 0
        )

        self._test_object.integer = TEST_OBJECT_INTEGER_VALUE
        self._test_object.save()

        id_list = self._do_backend_search(
            field_name='integer',
            query_type=QueryTypeExact,
            value=''
        )

        self.assertEqual(
            len(id_list), 0
        )

    def test_search_field_type_integer_null_search_exact_empty_quoted(self):
        self._test_object_integer_set = False

        id_list = self._do_backend_search(
            field_name='integer',
            is_quoted_value=True,
            query_type=QueryTypeExact,
            value=''
        )

        self.assertEqual(
            len(id_list), 0
        )

        self._test_object.integer = TEST_OBJECT_INTEGER_VALUE
        self._test_object.save()

        id_list = self._do_backend_search(
            field_name='integer',
            is_quoted_value=True,
            query_type=QueryTypeExact,
            value=''
        )

        self.assertEqual(
            len(id_list), 0
        )

    def test_search_field_type_integer_search_exact(self):
        id_list = self._do_backend_search(
            field_name='integer',
            query_type=QueryTypeExact,
            value=self._test_object.integer
        )

        self.assertEqual(
            len(id_list), 1
        )
        self.assertTrue(self._test_object.id in id_list)

        id_list = self._do_backend_search(
            field_name='integer',
            query_type=QueryTypeExact,
            value=str(self._test_object.integer)
        )

        self.assertEqual(
            len(id_list), 1
        )
        self.assertTrue(self._test_object.id in id_list)

        # Test valid value ranges.
        self._test_object.integer = -2 ** 31
        self._test_object.save()

        id_list = self._do_backend_search(
            field_name='integer',
            query_type=QueryTypeExact,
            value=str(self._test_object.integer)
        )

        self.assertEqual(
            len(id_list), 1
        )
        self.assertTrue(self._test_object.id in id_list)

        self._test_object.integer = 2 ** 31 - 1
        self._test_object.save()

        id_list = self._do_backend_search(
            field_name='integer',
            query_type=QueryTypeExact,
            value=str(self._test_object.integer)
        )

        self.assertEqual(
            len(id_list), 1
        )
        self.assertTrue(self._test_object.id in id_list)

    def test_search_field_type_integer_search_greater_than(self):
        id_list = self._do_backend_search(
            field_name='integer',
            query_type=QueryTypeGreaterThan,
            value=self._test_object.integer - 1
        )

        self.assertEqual(
            len(id_list), 1
        )
        self.assertTrue(self._test_object.id in id_list)

    def test_search_field_type_integer_search_greater_than_or_equal(self):
        id_list = self._do_backend_search(
            field_name='integer',
            query_type=QueryTypeGreaterThanOrEqual,
            value=self._test_object.integer - 1
        )

        self.assertEqual(
            len(id_list), 1
        )
        self.assertTrue(self._test_object.id in id_list)

        id_list = self._do_backend_search(
            field_name='integer',
            query_type=QueryTypeGreaterThanOrEqual,
            value=self._test_object.integer
        )

        self.assertEqual(
            len(id_list), 1
        )
        self.assertTrue(self._test_object.id in id_list)

    def test_search_field_type_integer_search_less_than(self):
        id_list = self._do_backend_search(
            field_name='integer',
            query_type=QueryTypeLessThan,
            value=self._test_object.integer + 1
        )

        self.assertEqual(
            len(id_list), 1
        )
        self.assertTrue(self._test_object.id in id_list)

    def test_search_field_type_integer_search_less_than_or_equal(self):
        id_list = self._do_backend_search(
            field_name='integer',
            query_type=QueryTypeLessThanOrEqual,
            value=self._test_object.integer + 1
        )

        self.assertEqual(
            len(id_list), 1
        )
        self.assertTrue(self._test_object.id in id_list)

        id_list = self._do_backend_search(
            field_name='integer',
            query_type=QueryTypeLessThanOrEqual,
            value=self._test_object.integer
        )

        self.assertEqual(
            len(id_list), 1
        )
        self.assertTrue(self._test_object.id in id_list)

    def test_search_field_type_integer_search_range(self):
        id_list = self._do_backend_search(
            field_name='integer',
            query_type=QueryTypeRange,
            value='{}..{}'.format(
                self._test_object.integer - 1, self._test_object.integer + 1
            )
        )

        self.assertEqual(
            len(id_list), 1
        )
        self.assertTrue(self._test_object.id in id_list)

        id_list = self._do_backend_search(
            field_name='integer',
            query_type=QueryTypeRange,
            value='{}..{}'.format(
                self._test_object.integer, self._test_object.integer + 1
            )
        )

        self.assertEqual(
            len(id_list), 1
        )
        self.assertTrue(self._test_object.id in id_list)

        id_list = self._do_backend_search(
            field_name='integer',
            query_type=QueryTypeRange,
            value='{}..{}'.format(
                self._test_object.integer - 1, self._test_object.integer
            )
        )

        self.assertEqual(
            len(id_list), 1
        )
        self.assertTrue(self._test_object.id in id_list)

        id_list = self._do_backend_search(
            field_name='integer',
            query_type=QueryTypeRange,
            value='{}..{}'.format(
                self._test_object.integer, self._test_object.integer
            )
        )

        self.assertEqual(
            len(id_list), 1
        )
        self.assertTrue(self._test_object.id in id_list)

    def test_search_field_type_integer_search_range_exclusive(self):
        id_list = self._do_backend_search(
            field_name='integer',
            query_type=QueryTypeRangeExclusive,
            value='{}..{}'.format(
                self._test_object.integer - 1, self._test_object.integer + 1
            )
        )

        self.assertEqual(
            len(id_list), 1
        )
        self.assertTrue(self._test_object.id in id_list)

        id_list = self._do_backend_search(
            field_name='integer',
            query_type=QueryTypeRangeExclusive,
            value='{}..{}'.format(
                self._test_object.integer, self._test_object.integer + 1
            )
        )

        self.assertEqual(
            len(id_list), 0
        )

        id_list = self._do_backend_search(
            field_name='integer',
            query_type=QueryTypeRangeExclusive,
            value='{}..{}'.format(
                self._test_object.integer - 1, self._test_object.integer
            )
        )

        self.assertEqual(
            len(id_list), 0
        )

        id_list = self._do_backend_search(
            field_name='integer',
            query_type=QueryTypeRangeExclusive,
            value='{}..{}'.format(
                self._test_object.integer, self._test_object.integer
            )
        )

        self.assertEqual(
            len(id_list), 0
        )

    def test_search_field_type_integer_search_range_exclusive_invalid(self):
        id_list = self._do_backend_search(
            field_name='integer',
            query_type=QueryTypeRangeExclusive,
            value='INVALID'
        )

        self.assertEqual(
            len(id_list), 0
        )

        id_list = self._do_backend_search(
            field_name='integer',
            query_type=QueryTypeRangeExclusive,
            value=True
        )

        self.assertEqual(
            len(id_list), 0
        )


class BackendFieldTypeQueryTypePositiveIntegerTestCaseMixin:
    def test_search_field_type_positiveinteger_search_exact_empty_non_quoted(self):
        id_list = self._do_backend_search(
            field_name='positiveinteger',
            query_type=QueryTypeExact,
            value=''
        )

        self.assertEqual(
            len(id_list), 0
        )

    def test_search_field_type_positiveinteger_search_exact(self):
        id_list = self._do_backend_search(
            field_name='positiveinteger',
            query_type=QueryTypeExact,
            value=self._test_object.positiveinteger
        )

        self.assertEqual(
            len(id_list), 1
        )
        self.assertTrue(self._test_object.id in id_list)

        id_list = self._do_backend_search(
            field_name='positiveinteger',
            query_type=QueryTypeExact,
            value=str(self._test_object.positiveinteger)
        )

        self.assertEqual(
            len(id_list), 1
        )
        self.assertTrue(self._test_object.id in id_list)

        # Test valid value range.
        self._test_object.positiveinteger = 2 ** 31 - 1
        self._test_object.save()

        id_list = self._do_backend_search(
            field_name='positiveinteger',
            query_type=QueryTypeExact,
            value=self._test_object.positiveinteger
        )

        self.assertEqual(
            len(id_list), 1
        )
        self.assertTrue(self._test_object.id in id_list)

    def test_search_field_type_positiveinteger_search_greater_than(self):
        id_list = self._do_backend_search(
            field_name='positiveinteger',
            query_type=QueryTypeGreaterThan,
            value=self._test_object.positiveinteger - 1
        )

        self.assertEqual(
            len(id_list), 1
        )
        self.assertTrue(self._test_object.id in id_list)

    def test_search_field_type_positiveinteger_search_greater_than_or_equal(self):
        id_list = self._do_backend_search(
            field_name='positiveinteger',
            query_type=QueryTypeGreaterThanOrEqual,
            value=self._test_object.positiveinteger - 1
        )

        self.assertEqual(
            len(id_list), 1
        )
        self.assertTrue(self._test_object.id in id_list)

        id_list = self._do_backend_search(
            field_name='positiveinteger',
            query_type=QueryTypeGreaterThanOrEqual,
            value=self._test_object.positiveinteger
        )

        self.assertEqual(
            len(id_list), 1
        )
        self.assertTrue(self._test_object.id in id_list)

    def test_search_field_type_positiveinteger_search_less_than(self):
        id_list = self._do_backend_search(
            field_name='positiveinteger',
            query_type=QueryTypeLessThan,
            value=self._test_object.positiveinteger + 1
        )

        self.assertEqual(
            len(id_list), 1
        )
        self.assertTrue(self._test_object.id in id_list)

    def test_search_field_type_positiveinteger_search_less_than_or_equal(self):
        id_list = self._do_backend_search(
            field_name='positiveinteger',
            query_type=QueryTypeLessThanOrEqual,
            value=self._test_object.positiveinteger + 1
        )

        self.assertEqual(
            len(id_list), 1
        )
        self.assertTrue(self._test_object.id in id_list)

        id_list = self._do_backend_search(
            field_name='positiveinteger',
            query_type=QueryTypeLessThanOrEqual,
            value=self._test_object.positiveinteger
        )

        self.assertEqual(
            len(id_list), 1
        )
        self.assertTrue(self._test_object.id in id_list)

    def test_search_field_type_positiveinteger_search_range(self):
        id_list = self._do_backend_search(
            field_name='positiveinteger',
            query_type=QueryTypeRange,
            value='{}..{}'.format(
                self._test_object.positiveinteger - 1, self._test_object.positiveinteger + 1
            )
        )

        self.assertEqual(
            len(id_list), 1
        )
        self.assertTrue(self._test_object.id in id_list)

        id_list = self._do_backend_search(
            field_name='positiveinteger',
            query_type=QueryTypeRange,
            value='{}..{}'.format(
                self._test_object.positiveinteger, self._test_object.positiveinteger + 1
            )
        )

        self.assertEqual(
            len(id_list), 1
        )
        self.assertTrue(self._test_object.id in id_list)

        id_list = self._do_backend_search(
            field_name='positiveinteger',
            query_type=QueryTypeRange,
            value='{}..{}'.format(
                self._test_object.positiveinteger - 1, self._test_object.positiveinteger
            )
        )

        self.assertEqual(
            len(id_list), 1
        )
        self.assertTrue(self._test_object.id in id_list)

        id_list = self._do_backend_search(
            field_name='positiveinteger',
            query_type=QueryTypeRange,
            value='{}..{}'.format(
                self._test_object.positiveinteger, self._test_object.positiveinteger
            )
        )

        self.assertEqual(
            len(id_list), 1
        )
        self.assertTrue(self._test_object.id in id_list)

    def test_search_field_type_positiveinteger_search_range_exclusive(self):
        id_list = self._do_backend_search(
            field_name='positiveinteger',
            query_type=QueryTypeRangeExclusive,
            value='{}..{}'.format(
                self._test_object.positiveinteger - 1, self._test_object.positiveinteger + 1
            )
        )

        self.assertEqual(
            len(id_list), 1
        )
        self.assertTrue(self._test_object.id in id_list)

        id_list = self._do_backend_search(
            field_name='positiveinteger',
            query_type=QueryTypeRangeExclusive,
            value='{}..{}'.format(
                self._test_object.positiveinteger, self._test_object.positiveinteger + 1
            )
        )

        self.assertEqual(
            len(id_list), 0
        )

        id_list = self._do_backend_search(
            field_name='positiveinteger',
            query_type=QueryTypeRangeExclusive,
            value='{}..{}'.format(
                self._test_object.positiveinteger - 1, self._test_object.positiveinteger
            )
        )

        self.assertEqual(
            len(id_list), 0
        )

        id_list = self._do_backend_search(
            field_name='positiveinteger',
            query_type=QueryTypeRangeExclusive,
            value='{}..{}'.format(
                self._test_object.positiveinteger, self._test_object.positiveinteger
            )
        )

        self.assertEqual(
            len(id_list), 0
        )

    def test_search_field_type_positiveinteger_search_range_exclusive_invalid(self):
        id_list = self._do_backend_search(
            field_name='positiveinteger',
            query_type=QueryTypeRangeExclusive,
            value='INVALID'
        )

        self.assertEqual(
            len(id_list), 0
        )

        id_list = self._do_backend_search(
            field_name='positiveinteger',
            query_type=QueryTypeRangeExclusive,
            value=True
        )

        self.assertEqual(
            len(id_list), 0
        )


class BackendFieldTypeQueryTypeTextTestCaseMixin:
    def test_search_field_type_text_search_exact_empty_non_quoted(self):
        id_list = self._do_backend_search(
            field_name='text',
            query_type=QueryTypeExact,
            value=''
        )

        self.assertEqual(
            len(id_list), 0
        )

    def test_search_field_type_text_search_exact_empty_quoted(self):
        id_list = self._do_backend_search(
            field_name='text',
            is_quoted_value=True,
            query_type=QueryTypeExact,
            value=''
        )

        self.assertEqual(
            len(id_list), 0
        )

        self._test_object.text = ''
        self._test_object.save()

        id_list = self._do_backend_search(
            field_name='text',
            is_quoted_value=True,
            query_type=QueryTypeExact,
            value=''
        )

        self.assertEqual(
            len(id_list), 1
        )
        self.assertTrue(self._test_object.id in id_list)

    def test_search_field_type_text_search_exact(self):
        id_list = self._do_backend_search(
            field_name='text',
            query_type=QueryTypeExact,
            value=self._test_object.text
        )

        self.assertEqual(
            len(id_list), 1
        )
        self.assertTrue(self._test_object.id in id_list)

    def test_search_field_type_text_search_fuzzy(self):
        id_list = self._do_backend_search(
            field_name='text',
            query_type=QueryTypeFuzzy,
            value='tetx'
        )

        self.assertEqual(
            len(id_list), 1
        )
        self.assertTrue(self._test_object.id in id_list)

        id_list = self._do_backend_search(
            field_name='text',
            is_quoted_value=True,
            query_type=QueryTypeFuzzy,
            value='test tetx'
        )

        self.assertEqual(
            len(id_list), 0
        )

    def test_search_field_type_text_search_partial(self):
        parts = self._test_object.text.split(' ')

        id_list = self._do_backend_search(
            field_name='text',
            query_type=QueryTypePartial,
            value=parts[0][:-1]
        )

        self.assertEqual(
            len(id_list), 1
        )
        self.assertTrue(self._test_object.id in id_list)

        id_list = self._do_backend_search(
            field_name='text',
            query_type=QueryTypePartial,
            value=parts[0][1:]
        )

        self.assertEqual(
            len(id_list), 1
        )
        self.assertTrue(self._test_object.id in id_list)

        id_list = self._do_backend_search(
            field_name='text',
            query_type=QueryTypePartial,
            value=parts[0].upper()[:-1]
        )

        self.assertEqual(
            len(id_list), 1
        )
        self.assertTrue(self._test_object.id in id_list)

        id_list = self._do_backend_search(
            field_name='text',
            query_type=QueryTypePartial,
            value=parts[0].upper()[1:]
        )

        self.assertEqual(
            len(id_list), 1
        )
        self.assertTrue(self._test_object.id in id_list)

        id_list = self._do_backend_search(
            field_name='text',
            is_quoted_value=True,
            query_type=QueryTypePartial,
            value=' '.join((parts[0], parts[1]))
        )

        self.assertEqual(
            len(id_list), 1
        )
        self.assertTrue(self._test_object.id in id_list)

        id_list = self._do_backend_search(
            field_name='text',
            is_quoted_value=True,
            query_type=QueryTypePartial,
            value=' '.join((parts[1], parts[0]))
        )

        self.assertEqual(
            len(id_list), 0
        )

        id_list = self._do_backend_search(
            field_name='text',
            is_quoted_value=True,
            query_type=QueryTypePartial,
            value=' '.join((parts[0], parts[2]))
        )

        self.assertEqual(
            len(id_list), 0
        )

    def test_search_field_type_text_search_regular_expression(self):
        id_list = self._do_backend_search(
            field_name='text',
            query_type=QueryTypeRegularExpression,
            value='t.*t'
        )

        self.assertEqual(
            len(id_list), 1
        )
        self.assertTrue(self._test_object.id in id_list)

        id_list = self._do_backend_search(
            field_name='text',
            query_type=QueryTypeRegularExpression,
            value='(text|INVALID)'
        )

        self.assertEqual(
            len(id_list), 1
        )
        self.assertTrue(self._test_object.id in id_list)

    def test_search_field_type_text_search_regular_expression_invalid(self):
        id_list = self._do_backend_search(
            field_name='text',
            query_type=QueryTypeRegularExpression,
            value=99
        )

        self.assertEqual(
            len(id_list), 0
        )


class BackendFieldTypeQueryTypeUUIDTestCaseMixin:
    def test_search_field_type_uuid_search_exact_empty_non_quoted(self):
        id_list = self._do_backend_search(
            field_name='uuid',
            query_type=QueryTypeExact,
            value=''
        )

        self.assertEqual(
            len(id_list), 0
        )

    def test_search_field_type_uuid_search_exact(self):
        id_list = self._do_backend_search(
            field_name='uuid',
            query_type=QueryTypeExact,
            value=self._test_object.uuid
        )

        self.assertEqual(
            len(id_list), 1
        )
        self.assertTrue(self._test_object.id in id_list)

    def test_search_field_type_uuid_search_partial(self):
        id_list = self._do_backend_search(
            field_name='uuid',
            query_type=QueryTypePartial,
            value=str(self._test_object.uuid)[1:-1]
        )

        self.assertEqual(
            len(id_list), 1
        )
        self.assertTrue(self._test_object.id in id_list)

        id_list = self._do_backend_search(
            field_name='uuid',
            query_type=QueryTypePartial,
            value=str(self._test_object.uuid).split('-')[0]
        )

        self.assertEqual(
            len(id_list), 1
        )
        self.assertTrue(self._test_object.id in id_list)

    def test_search_field_type_uuid_search_regular_expression(self):
        parts = str(self._test_object.uuid).split('-')

        id_list = self._do_backend_search(
            field_name='uuid',
            query_type=QueryTypeRegularExpression,
            value='{}.*{}.*'.format(parts[0][:5], parts[0][-1])
        )

        self.assertEqual(
            len(id_list), 1
        )
        self.assertTrue(self._test_object.id in id_list)

        id_list = self._do_backend_search(
            field_name='uuid',
            query_type=QueryTypeRegularExpression,
            value='({}|INVALID)'.format(
                '{}.*{}.*'.format(parts[0][:5], parts[0][-1])
            )
        )

        self.assertEqual(
            len(id_list), 1
        )
        self.assertTrue(self._test_object.id in id_list)

    def test_search_field_type_uuid_search_exact_invalid(self):
        id_list = self._do_backend_search(
            field_name='uuid',
            query_type=QueryTypeExact,
            value=True
        )

        self.assertEqual(
            len(id_list), 0
        )

    def test_search_field_type_uuid_search_regular_expression_invalid(self):
        id_list = self._do_backend_search(
            field_name='uuid',
            query_type=QueryTypeRegularExpression,
            value=True
        )

        self.assertEqual(
            len(id_list), 0
        )


class BackendFieldTypeQueryTypeTestCaseMixin(
    BackendFieldTypeQueryTypeAnyTestCaseMixin,
    BackendFieldTypeQueryTypeAutoFieldTestCaseMixin,
    BackendFieldTypeQueryTypeBooleanTestCaseMixin,
    BackendFieldTypeQueryTypeCharTestCaseMixin,
    BackendFieldTypeQueryTypeDateTimeTestCaseMixin,
    BackendFieldTypeQueryTypeEmailTestCaseMixin,
    BackendFieldTypeQueryTypeIntegerTestCaseMixin,
    BackendFieldTypeQueryTypePositiveIntegerTestCaseMixin,
    BackendFieldTypeQueryTypeTextTestCaseMixin,
    BackendFieldTypeQueryTypeUUIDTestCaseMixin,
    BackendSearchTestMixin, TestSearchObjectSimpleTestMixin,
    SearchTestMixin
):
    """
    Consolidated backend test field type and query type case mixin.
    """
