from ...literals import QUERY_PARAMETER_ANY_FIELD
from ...search_query_types import QueryTypeExact, QueryTypePartial
from ...settings import setting_results_limit

from .backend_mixins import BackendSearchTestMixin
from .base import SearchTestMixin, TestSearchObjectHierarchyTestMixin


class BackendSearchFieldAnyFieldTestCaseMixin:
    def test_any_field_hyphenated_value(self):
        self._test_object.label = 'P01208-06'
        self._test_object.save()

        id_list = self._do_backend_search(
            field_name=QUERY_PARAMETER_ANY_FIELD,
            query_type=QueryTypePartial,
            value='P01208-06'
        )

        self.assertEqual(len(id_list), 1)
        self.assertTrue(self._test_object.id in id_list)

        id_list = self._do_backend_search(
            field_name=QUERY_PARAMETER_ANY_FIELD,
            query_type=QueryTypePartial,
            value='P01208'
        )

        self.assertEqual(len(id_list), 1)
        self.assertTrue(self._test_object.id in id_list)

        id_list = self._do_backend_search(
            field_name=QUERY_PARAMETER_ANY_FIELD,
            query_type=QueryTypePartial,
            value='06'
        )

        self.assertEqual(len(id_list), 1)
        self.assertTrue(self._test_object.id in id_list)

    def test_any_field_hyphenated_value_mixed(self):
        self._test_object.label = 'P01208-06 word'
        self._test_object.save()

        id_list = self._do_backend_search(
            field_name=QUERY_PARAMETER_ANY_FIELD,
            query_type=QueryTypePartial,
            value='P01208-06'
        )

        self.assertEqual(len(id_list), 1)
        self.assertTrue(self._test_object.id in id_list)

        id_list = self._do_backend_search(
            field_name=QUERY_PARAMETER_ANY_FIELD,
            query_type=QueryTypePartial,
            value='word'
        )

        self.assertEqual(len(id_list), 1)
        self.assertTrue(self._test_object.id in id_list)

    def test_any_field_invalid_value(self):
        id_list = self._do_backend_search(
            field_name=QUERY_PARAMETER_ANY_FIELD,
            query_type=QueryTypePartial,
            value='invalid'
        )

        self.assertEqual(len(id_list), 0)
        self.assertTrue(self._test_object.id not in id_list)


class BackendSearchFieldDirectFieldTestCaseMixin:
    def test_direct_field_case_insensitive_search(self):
        self._test_object.label = self._test_object.label.upper()
        self._test_object.save()

        id_list = self._do_backend_search(
            field_name='label',
            query_type=QueryTypeExact,
            value=self._test_object.label.lower()
        )

        self.assertEqual(len(id_list), 1)
        self.assertTrue(self._test_object.id in id_list)

        self._test_object.label = self._test_object.label.lower()
        self._test_object.save()

        id_list = self._do_backend_search(
            field_name='label',
            query_type=QueryTypeExact,
            value=self._test_object.label.upper()
        )

        self.assertEqual(len(id_list), 1)
        self.assertTrue(self._test_object.id in id_list)

    def test_direct_field_partial_search(self):
        id_list = self._do_backend_search(
            field_name='label',
            query_type=QueryTypePartial,
            value=self._test_object.label[0:4]
        )

        self.assertEqual(len(id_list), 1)
        self.assertTrue(self._test_object.id in id_list)

    def test_direct_field_partial_case_insensitive_search(self):
        id_list = self._do_backend_search(
            field_name='label',
            query_type=QueryTypePartial,
            value=self._test_object.label.upper()[0:4]
        )

        self.assertEqual(len(id_list), 1)
        self.assertTrue(self._test_object.id in id_list)

    def test_direct_field_search(self):
        id_list = self._do_backend_search(
            field_name='label', query_type=QueryTypeExact,
            value=self._test_object.label
        )

        self.assertEqual(len(id_list), 1)
        self.assertTrue(self._test_object.id in id_list)

    def test_direct_field_exact_search(self):
        self._test_object.label = '123-456-789'
        self._test_object.save()

        id_list = self._do_backend_search(
            field_name='label',
            query_type=QueryTypeExact,
            value='123'
        )

        self.assertEqual(len(id_list), 0)

        id_list = self._do_backend_search(
            field_name='label', query_type=QueryTypeExact,
            value='123-456'
        )

        self.assertEqual(len(id_list), 0)

        id_list = self._do_backend_search(
            field_name='label', query_type=QueryTypeExact,
            value='123-456-789'
        )

        self.assertEqual(len(id_list), 1)
        self.assertTrue(self._test_object.id in id_list)

    def test_direct_field_update_search(self):
        old_label = self._test_object.label
        self._test_object.label = 'edited'
        self._test_object.save()

        id_list = self._do_backend_search(
            field_name='label', query_type=QueryTypeExact,
            value=self._test_object.label
        )

        self.assertEqual(len(id_list), 1)
        self.assertTrue(self._test_object.id in id_list)

        id_list = self._do_backend_search(
            field_name='label', query_type=QueryTypeExact,
            value=old_label
        )

        self.assertEqual(len(id_list), 0)

    def test_direct_field_delete_search(self):
        self._test_object.delete()

        id_list = self._do_backend_search(
            field_name='label', query_type=QueryTypeExact,
            value=self._test_object.label
        )

        self.assertEqual(len(id_list), 0)


class BackendLimitTestCase:
    def test_setting_search_results_limit(self):
        self._test_search_model = self._test_search_grandchild

        id_list = self._do_backend_search(
            field_name='label', query_type=QueryTypePartial,
            value='grandchild'
        )

        self.assertEqual(len(id_list), 2)
        self.assertTrue(self._test_object_grandchildren[0].id in id_list)
        self.assertTrue(self._test_object_grandchildren[1].id in id_list)

        setting_results_limit.set(value=1)

        id_list = self._do_backend_search(
            field_name='label', query_type=QueryTypePartial,
            value='grandchild'
        )

        self.assertEqual(len(id_list), 1)

        id_list = self._do_backend_search(
            field_name='label', limit=3,
            query_type=QueryTypePartial, value='grandchild'
        )

        self.assertEqual(len(id_list), 2)
        self.assertTrue(self._test_object_grandchildren[0].id in id_list)
        self.assertTrue(self._test_object_grandchildren[1].id in id_list)


class BackendSearchFieldManyToManyFieldTestCaseMixin:
    def test_direct_many_to_many_search(self):
        self._test_search_model = self._test_search_grandchild

        id_list = self._do_backend_search(
            field_name='attributes__label',
            query_type=QueryTypeExact,
            value=self._test_object_attribute.label
        )

        self.assertEqual(len(id_list), 1)
        self.assertTrue(self._test_object_grandchild.id in id_list)

    def test_direct_many_to_many_delete_search(self):
        self._test_search_model = self._test_search_grandchild

        self._test_object_attribute.delete()

        id_list = self._do_backend_search(
            field_name='attributes__label',
            query_type=QueryTypeExact,
            value=self._test_object_attribute.label
        )

        self.assertEqual(len(id_list), 0)
        self.assertTrue(self._test_object_grandchild.id not in id_list)

    def test_direct_many_to_many_updated_search(self):
        self._test_search_model = self._test_search_grandchild

        old_label_value = self._test_object_attribute.label
        self._test_object_attribute.label = 'edited'
        self._test_object_attribute.save()

        id_list = self._do_backend_search(
            field_name='attributes__label',
            query_type=QueryTypeExact,
            value=self._test_object_attribute.label
        )

        self.assertEqual(len(id_list), 1)
        self.assertTrue(self._test_object_grandchild.id in id_list)

        id_list = self._do_backend_search(
            field_name='attributes__label',
            query_type=QueryTypeExact, value=old_label_value
        )

        self.assertEqual(len(id_list), 0)
        self.assertTrue(self._test_object_grandchild.id not in id_list)

    def test_direct_many_to_many_remove_search(self):
        self._test_search_model = self._test_search_grandchild

        self._test_object_grandchild.attributes.remove(
            self._test_object_attribute
        )

        id_list = self._do_backend_search(
            field_name='attributes__label',
            query_type=QueryTypeExact,
            value=self._test_object_attribute.label
        )

        self.assertEqual(len(id_list), 0)
        self.assertTrue(self._test_object_grandchild.id not in id_list)

    def test_reverse_many_to_many_search(self):
        self._test_search_model = self._test_search_attribute

        id_list = self._do_backend_search(
            field_name='children__label',
            query_type=QueryTypeExact,
            value=self._test_object_grandchild.label
        )

        self.assertEqual(len(id_list), 1)
        self.assertTrue(self._test_object_attribute.id in id_list)

    def test_reverse_many_to_many_parent_delete_search(self):
        self._test_search_model = self._test_search_attribute

        self._test_object_grandchild.delete()

        id_list = self._do_backend_search(
            field_name='children__label',
            query_type=QueryTypeExact,
            value=self._test_object_grandchild.label
        )

        self.assertEqual(len(id_list), 0)
        self.assertTrue(self._test_object_attribute.id not in id_list)


class BackendProxyObjectTestCaseMixin:
    def test_proxy_object_field_update_search(self):
        self._test_search_model = self._test_search_grandchild

        old_label = self._test_object_grandchild_proxy.label
        self._test_object_grandchild_proxy.label = 'edited'
        self._test_object_grandchild_proxy.save()

        id_list = self._do_backend_search(
            field_name='label',
            query_type=QueryTypeExact,
            value=self._test_object_grandchild_proxy.label
        )

        self.assertEqual(len(id_list), 1)
        self.assertTrue(self._test_object_grandchild.id in id_list)

        id_list = self._do_backend_search(
            field_name='label', query_type=QueryTypeExact,
            value=old_label
        )

        self.assertEqual(len(id_list), 0)
        self.assertTrue(self._test_object_grandchild.id not in id_list)

    def test_proxy_object_delete_search(self):
        self._test_search_model = self._test_search_grandchild

        id_list = self._do_backend_search(
            field_name='label', query_type=QueryTypeExact,
            value=self._test_object_grandchild.label
        )

        self.assertEqual(len(id_list), 1)
        self.assertTrue(self._test_object_grandchild.id in id_list)

        self._test_object_grandchild_proxy.delete()

        id_list = self._do_backend_search(
            field_name='label', query_type=QueryTypeExact,
            value=self._test_object_grandchild.label
        )

        self.assertEqual(len(id_list), 0)
        self.assertTrue(self._test_object_grandchild.id not in id_list)

    def test_proxy_object_many_to_many_remove_search(self):
        self._test_search_model = self._test_search_grandchild

        id_list = self._do_backend_search(
            field_name='attributes__label',
            query_type=QueryTypeExact,
            value=self._test_object_attribute.label
        )

        self.assertEqual(len(id_list), 1)
        self.assertTrue(self._test_object_grandchild.id in id_list)

        self._test_object_grandchild_proxy.attributes.remove(
            self._test_object_attribute
        )

        id_list = self._do_backend_search(
            field_name='attributes__label',
            query_type=QueryTypeExact,
            value=self._test_object_attribute.label
        )

        self.assertEqual(len(id_list), 0)
        self.assertTrue(self._test_object_grandchild.id not in id_list)


class BackendSearchFieldRelatedObjectDirectFieldTestCaseMixin:
    def test_related_field_search(self):
        self._test_search_model = self._test_search_grandparent

        id_list = self._do_backend_search(
            field_name='children__label',
            query_type=QueryTypeExact,
            value=self._test_object_parent.label
        )

        self.assertEqual(len(id_list), 1)
        self.assertTrue(self._test_object_grandparent.id in id_list)

    def test_related_field_delete_search(self):
        self._test_search_model = self._test_search_grandparent

        self._test_object_parent.delete()

        id_list = self._do_backend_search(
            field_name='children__label',
            query_type=QueryTypeExact,
            value=self._test_object_parent.label
        )

        self.assertEqual(len(id_list), 0)
        self.assertTrue(self._test_object_grandparent.id not in id_list)

    def test_related_field_update_search(self):
        self._test_search_model = self._test_search_grandparent

        old_label_value = self._test_object_parent.label
        self._test_object_parent.label = 'edited'
        self._test_object_parent.save()

        id_list = self._do_backend_search(
            field_name='children__label',
            query_type=QueryTypeExact,
            value=self._test_object_parent.label
        )

        self.assertEqual(len(id_list), 1)
        self.assertTrue(self._test_object_grandparent.id in id_list)

        id_list = self._do_backend_search(
            field_name='children__label',
            query_type=QueryTypeExact,
            value=old_label_value
        )

        self.assertEqual(len(id_list), 0)
        self.assertTrue(self._test_object_grandparent.id not in id_list)

    def test_related_field_multiple_level_search(self):
        self._test_search_model = self._test_search_grandparent

        id_list = self._do_backend_search(
            field_name='children__children__label',
            query_type=QueryTypeExact,
            value=self._test_object_grandchild.label
        )

        self.assertEqual(len(id_list), 1)
        self.assertTrue(self._test_object_grandparent.id in id_list)

    def test_related_field_multiple_level_delete_search(self):
        self._test_search_model = self._test_search_grandparent

        self._test_object_grandchild.delete()

        id_list = self._do_backend_search(
            field_name='children__children__label',
            query_type=QueryTypeExact,
            value=self._test_object_grandchild.label
        )

        self.assertEqual(len(id_list), 0)
        self.assertTrue(self._test_object_grandparent.id not in id_list)

    def test_related_field_multiple_level_update_search(self):
        self._test_search_model = self._test_search_grandparent

        old_label_value = self._test_object_grandchild.label
        self._test_object_grandchild.label = 'edited'
        self._test_object_grandchild.save()

        id_list = self._do_backend_search(
            field_name='children__children__label',
            query_type=QueryTypeExact,
            value=self._test_object_grandchild.label
        )

        self.assertEqual(len(id_list), 1)
        self.assertTrue(self._test_object_grandparent.id in id_list)

        id_list = self._do_backend_search(
            field_name='children__children__label',
            query_type=QueryTypeExact,
            value=old_label_value
        )

        self.assertEqual(len(id_list), 0)
        self.assertTrue(self._test_object_grandparent.id not in id_list)


class BackendSearchFieldRelatedObjectManyToManyFieldTestCaseMixin:
    def test_related_field_multiple_level_many_to_many_search(self):
        self._test_search_model = self._test_search_grandparent

        id_list = self._do_backend_search(
            field_name='children__children__attributes__label',
            query_type=QueryTypeExact,
            value=self._test_object_attribute.label
        )

        self.assertEqual(len(id_list), 1)
        self.assertTrue(self._test_object_grandparent.id in id_list)

    def test_related_field_multiple_level_many_to_many_delete_search(self):
        self._test_search_model = self._test_search_grandparent

        self._test_object_attribute.delete()

        id_list = self._do_backend_search(
            field_name='children__children__attributes__label',
            query_type=QueryTypeExact,
            value=self._test_object_attribute.label
        )

        self.assertEqual(len(id_list), 0)
        self.assertTrue(self._test_object_grandparent.id not in id_list)

    def test_related_field_multiple_level_many_to_many_updated_search(self):
        self._test_search_model = self._test_search_grandparent

        old_label_value = self._test_object_attribute.label
        self._test_object_attribute.label = 'edited'
        self._test_object_attribute.save()

        id_list = self._do_backend_search(
            field_name='children__children__attributes__label',
            query_type=QueryTypeExact,
            value=self._test_object_attribute.label
        )

        self.assertEqual(len(id_list), 1)
        self.assertTrue(self._test_object_grandparent.id in id_list)

        id_list = self._do_backend_search(
            field_name='children__children__attributes__label',
            query_type=QueryTypeExact,
            value=old_label_value
        )

        self.assertEqual(len(id_list), 0)
        self.assertTrue(self._test_object_grandparent.id not in id_list)

    def test_related_field_multiple_level_many_to_many_remove_search(self):
        self._test_search_model = self._test_search_grandparent

        self._test_object_grandchild.attributes.remove(
            self._test_object_attribute
        )

        id_list = self._do_backend_search(
            field_name='children__children__attributes__label',
            query_type=QueryTypeExact,
            value=self._test_object_attribute.label
        )

        self.assertEqual(len(id_list), 0)
        self.assertTrue(self._test_object_grandparent.id not in id_list)


class BackendSearchFieldTestCaseMixin(
    BackendLimitTestCase, BackendProxyObjectTestCaseMixin,
    BackendSearchFieldAnyFieldTestCaseMixin,
    BackendSearchFieldDirectFieldTestCaseMixin,
    BackendSearchFieldManyToManyFieldTestCaseMixin,
    BackendSearchFieldRelatedObjectDirectFieldTestCaseMixin,
    BackendSearchFieldRelatedObjectManyToManyFieldTestCaseMixin,
    BackendSearchTestMixin, TestSearchObjectHierarchyTestMixin,
    SearchTestMixin
):
    """
    Consolidated backend test case mixin.
    """
