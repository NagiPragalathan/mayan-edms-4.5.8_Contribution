from django.db import models

from mayan.apps.testing.tests.base import BaseTestCase

from ..search_models import SearchModel

from .mixins.base import SearchTestMixin


class SearchModelTestCase(SearchTestMixin, BaseTestCase):
    auto_test_search_objects_create = False

    def _create_test_models(self):
        self._TestModel = self._create_test_model(
            fields={
                'label': models.CharField(
                    max_length=32
                )
            }, model_name='TestModel'
        )

    def _setup_test_model_search(self):
        self._test_search_model = SearchModel(
            app_label=self._TestModel._meta.app_label,
            model_name=self._TestModel._meta.model_name
        )
        self._test_search_model.add_model_field(
            field='label'
        )

    def test_search_field_removal(self):
        test_search_fields = self._test_search_model.search_fields

        test_search_field = self._test_search_model.get_search_field(
            field_name='label'
        )

        self._test_search_model.remove_search_field(
            search_field=test_search_field
        )

        self.assertNotEqual(
            self._test_search_model.search_fields, test_search_fields
        )
