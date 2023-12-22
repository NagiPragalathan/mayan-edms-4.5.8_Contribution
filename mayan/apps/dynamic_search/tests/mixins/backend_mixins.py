from ...settings import setting_results_limit


class BackendSearchTestMixin:
    _test_search_model = None

    def _do_backend_search(
        self, field_name, query_type, value, limit=None,
        is_quoted_value=False, is_raw_value=False, _skip_refresh=None
    ):
        limit = limit or setting_results_limit.value
        search_field = self._test_search_model.get_search_field(
            field_name=field_name
        )

        return self._test_search_backend._search(
            is_quoted_value=is_quoted_value, is_raw_value=is_raw_value,
            limit=limit, query_type=query_type, search_field=search_field,
            value=value, _skip_refresh=_skip_refresh
        )

    def _do_search(self, query):
        self._test_search_backend.refresh()

        return self._test_search_backend.search(
            search_model=self._test_search_model, query=query,
            user=self._test_case_user
        )
