from collections import deque
import functools
import logging

import elasticsearch
from elasticsearch import Elasticsearch, helpers
import elasticsearch_dsl
from elasticsearch_dsl import MultiSearch, Q, Search

from ..exceptions import (
    DynamicSearchBackendException, DynamicSearchValueTransformationError
)
from ..search_backends import SearchBackend
from ..search_fields import SearchFieldVirtualAllFields
from ..search_models import SearchModel
from ..search_query_types import (
    BackendQueryType, QueryTypeExact, QueryTypeFuzzy, QueryTypeGreaterThan,
    QueryTypeGreaterThanOrEqual, QueryTypeLessThan,
    QueryTypeLessThanOrEqual, QueryTypePartial, QueryTypeRange,
    QueryTypeRangeExclusive, QueryTypeRegularExpression
)

from .literals.elasticsearch_literals import (
    DEFAULT_ELASTICSEARCH_CLIENT_MAXSIZE,
    DEFAULT_ELASTICSEARCH_CLIENT_SNIFF_ON_START,
    DEFAULT_ELASTICSEARCH_CLIENT_SNIFF_ON_CONNECTION_FAIL,
    DEFAULT_ELASTICSEARCH_CLIENT_SNIFFER_TIMEOUT, DEFAULT_ELASTICSEARCH_HOST,
    DEFAULT_ELASTICSEARCH_INDICES_NAMESPACE,
    DJANGO_TO_ELASTICSEARCH_FIELD_MAP,
    MAXIMUM_API_ATTEMPT_COUNT
)

logger = logging.getLogger(name=__name__)


class BackendQueryTypeExact(BackendQueryType):
    query_type = QueryTypeExact

    def do_resolve(self):
        if self.value is not None:
            if self.is_quoted_value:
                template = '"{}"'
            else:
                template = '{}'

            if not self.value:
                # Empty values cannot be quoted.
                template = '{}'

                if self.is_quoted_value:
                    if self.get_search_backend_field_type() == elasticsearch_dsl.field.Text:
                        return Q(
                            'bool', must_not=(
                                Q(
                                    'wildcard',
                                    **{self.search_field.field_name: '*'}
                                )
                            )
                        )

            if self.is_quoted_value:
                return Q(
                    name_or_query='match_phrase', _expand__to_dot=False,
                    **{self.search_field.field_name: template.format(self.value)}
                )
            else:
                return Q(
                    name_or_query='match', _expand__to_dot=False,
                    **{self.search_field.field_name: template.format(self.value)}
                )


class BackendQueryFuzzy(BackendQueryType):
    query_type = QueryTypeFuzzy

    def do_resolve(self):
        if self.value is not None:
            return Q(
                name_or_query='fuzzy', _expand__to_dot=False,
                **{self.search_field.field_name: self.value}
            )


class BackendQueryTypeGreaterThan(BackendQueryType):
    query_type = QueryTypeGreaterThan

    def do_resolve(self):
        if self.value is not None:
            return Q(
                name_or_query='range', _expand__to_dot=False,
                **{self.search_field.field_name: {'gt': self.value}}
            )


class BackendQueryTypeGreaterThanOrEqual(BackendQueryType):
    query_type = QueryTypeGreaterThanOrEqual

    def do_resolve(self):
        if self.value is not None:
            return Q(
                name_or_query='range', _expand__to_dot=False,
                **{self.search_field.field_name: {'gte': self.value}}
            )


class BackendQueryTypeLessThan(BackendQueryType):
    query_type = QueryTypeLessThan

    def do_resolve(self):
        if self.value is not None:
            return Q(
                name_or_query='range', _expand__to_dot=False,
                **{self.search_field.field_name: {'lt': self.value}}
            )


class BackendQueryTypeLessThanOrEqual(BackendQueryType):
    query_type = QueryTypeLessThanOrEqual

    def do_resolve(self):
        if self.value is not None:
            return Q(
                name_or_query='range', _expand__to_dot=False,
                **{self.search_field.field_name: {'lte': self.value}}
            )


class BackendQueryTypePartial(BackendQueryType):
    query_type = QueryTypePartial

    def do_resolve(self):
        if self.value is not None:
            if self.get_search_backend_field_type() != elasticsearch_dsl.field.Date:
                if self.is_quoted_value:
                    return Q(
                        name_or_query='match_phrase', _expand__to_dot=False,
                        **{self.search_field.field_name: '{}'.format(self.value)}
                    )
                else:
                    if self.get_search_backend_field_type() != elasticsearch_dsl.field.Integer:
                        return Q(
                            name_or_query='wildcard', _expand__to_dot=False,
                            **{self.search_field.field_name: '*{}*'.format(self.value)}
                        )


class BackendQueryTypeRange(BackendQueryType):
    query_type = QueryTypeRange

    def do_resolve(self):
        if self.value is not None:
            return Q(
                name_or_query='range', _expand__to_dot=False,
                **{
                    self.search_field.field_name: {
                        'gte': self.value[0], 'lte': self.value[1]
                    }
                }
            )


class BackendQueryTypeRangeExclusive(BackendQueryType):
    query_type = QueryTypeRangeExclusive

    def do_resolve(self):
        if self.value is not None:
            return Q(
                name_or_query='range', _expand__to_dot=False,
                **{
                    self.search_field.field_name: {
                        'gt': self.value[0], 'lt': self.value[1]
                    }
                }
            )


class BackendQueryTypeRegularExpression(BackendQueryType):
    query_type = QueryTypeRegularExpression

    def do_resolve(self):
        if self.value is not None:
            return Q(
                name_or_query='regexp', _expand__to_dot=False,
                **{self.search_field.field_name: self.value}
            )


class ElasticSearchBackend(SearchBackend):
    feature_reindex = True
    field_type_mapping = DJANGO_TO_ELASTICSEARCH_FIELD_MAP

    def __init__(
        self, client_http_auth=None, client_host=DEFAULT_ELASTICSEARCH_HOST,
        client_hosts=None,
        client_maxsize=DEFAULT_ELASTICSEARCH_CLIENT_MAXSIZE,
        client_port=None, client_scheme=None,
        client_sniff_on_connection_fail=DEFAULT_ELASTICSEARCH_CLIENT_SNIFF_ON_CONNECTION_FAIL,
        client_sniff_on_start=DEFAULT_ELASTICSEARCH_CLIENT_SNIFF_ON_START,
        client_sniffer_timeout=DEFAULT_ELASTICSEARCH_CLIENT_SNIFFER_TIMEOUT,
        indices_namespace=DEFAULT_ELASTICSEARCH_INDICES_NAMESPACE,
        **kwargs
    ):
        super().__init__(**kwargs)

        self.indices_namespace = indices_namespace

        self.client_kwargs = {
            'hosts': client_hosts or (client_host,),
            'http_auth': client_http_auth, 'maxsize': client_maxsize,
            'port': client_port, 'scheme': client_scheme,
            'sniff_on_start': client_sniff_on_start,
            'sniff_on_connection_fail': client_sniff_on_connection_fail,
            'sniffer_timeout': client_sniffer_timeout
        }

        if self._test_mode:
            self.indices_namespace = 'mayan-test'

    def _do_response_process(self, response):
        result = set()

        for hit in response:
            result.add(int(hit['id']))

        return result

    def do_search_execute(self, search):
        try:
            return search.execute()
        except elasticsearch.exceptions.NotFoundError as exception:
            raise DynamicSearchBackendException(
                'Index not found. Make sure the search engine '
                'was properly initialized or upgraded if '
                'it already existed.'
            ) from exception

    def _get_client(self):
        return Elasticsearch(**self.client_kwargs)

    def _get_index_name(self, search_model):
        return '{}-{}'.format(
            self.indices_namespace, search_model.model_name.lower()
        )

    @functools.cache
    def _get_search_model_index_mappings(self, search_model):
        mappings = {}

        field_map = self.get_resolved_field_type_map(
            search_model=search_model
        )
        for field_name, search_field_data in field_map.items():
            mappings[field_name] = {
                'type': search_field_data['field'].name
            }

            if 'analyzer' in search_field_data:
                mappings[field_name]['analyzer'] = search_field_data['analyzer']

        return mappings

    def _get_status(self):
        client = self._get_client()
        result = []

        title = 'Elastic Search search model indexing status'
        result.append(title)
        result.append(len(title) * '=')

        self.refresh()

        for search_model in SearchModel.all():
            index_name = self._get_index_name(search_model=search_model)
            try:
                index_stats = client.count(index=index_name)
            except elasticsearch.exceptions.NotFoundError:
                index_stats = {}

            count = index_stats.get('count', 'None')

            result.append(
                '{}: {}'.format(search_model.label, count)
            )

        return '\n'.join(result)

    def _initialize(self):
        self._update_mappings()

    def _search(
        self, limit, search_field, query_type, value, is_quoted_value=False,
        is_raw_value=False
    ):
        self.do_query_type_verify(
            query_type=query_type, search_field=search_field
        )

        client = self._get_client()
        index_name = self._get_index_name(
            search_model=search_field.search_model
        )

        if isinstance(search_field, SearchFieldVirtualAllFields):
            multi_search = MultiSearch(index=index_name, using=client)

            for search_field in search_field.field_composition:
                try:
                    search_field_query = query_type.resolve_for_backend(
                        is_quoted_value=is_quoted_value,
                        is_raw_value=is_raw_value, search_backend=self,
                        search_field=search_field, value=value
                    )
                except DynamicSearchValueTransformationError:
                    """Skip the search field."""
                else:
                    if search_field_query is not None:
                        index_name = self._get_index_name(
                            search_model=search_field.search_model
                        )

                        multi_search = multi_search.add(
                            Search().query(
                                search_field_query
                            )
                        )

            if multi_search.to_dict():
                responses = self.do_search_execute(search=multi_search)
                result = set()

                for response in responses:
                    result.update(
                        self._do_response_process(response=response)
                    )

                return result
            else:
                return ()
        else:
            search = Search(index=index_name, using=client)

            try:
                search_field_query = query_type.resolve_for_backend(
                    is_quoted_value=is_quoted_value,
                    is_raw_value=is_raw_value, search_backend=self,
                    search_field=search_field, value=value
                )
            except DynamicSearchValueTransformationError:
                return ()
            else:
                if search_field_query is None:
                    return ()
                else:
                    search = search.source(None).query(search_field_query)
                    response = self.do_search_execute(search=search[0:limit])
                    return self._do_response_process(response=response)

    def _update_mappings(self, search_model=None):
        client = self._get_client()

        if search_model:
            search_models = (search_model,)
        else:
            search_models = SearchModel.all()

        for search_model in search_models:
            index_name = self._get_index_name(search_model=search_model)

            mappings = self._get_search_model_index_mappings(
                search_model=search_model
            )

            try:
                client.indices.delete(index=index_name)
            except elasticsearch.exceptions.NotFoundError:
                """
                Non fatal, might be that this is the first time
                the method is executed. Proceed.
                """

            try:
                client.indices.create(
                    index=index_name,
                    body={
                        'mappings': {
                            'properties': mappings
                        }
                    }
                )
            except elasticsearch.exceptions.RequestError:
                try:
                    client.indices.put_mapping(
                        index=index_name,
                        body={
                            'properties': mappings
                        }
                    )
                except elasticsearch.exceptions.RequestError:
                    """
                    There are mapping changes that were not allowed.
                    Example: Text to Keyword.
                    Boot up regardless and allow user to reindex to delete
                    old indices.
                    """

    def deindex_instance(self, instance):
        search_model = SearchModel.get_for_model(instance=instance)
        client = self._get_client()
        client.delete(
            id=instance.pk,
            index=self._get_index_name(search_model=search_model)
        )

    def index_instance(self, instance, exclude_model=None, exclude_kwargs=None):
        search_model = SearchModel.get_for_model(instance=instance)

        document = search_model.populate(
            search_backend=self, instance=instance, exclude_model=exclude_model,
            exclude_kwargs=exclude_kwargs
        )
        self._get_client().index(
            index=self._get_index_name(search_model=search_model),
            id=instance.pk, document=document
        )

    def index_instances(self, search_model, id_list):
        client = self._get_client()
        index_name = self._get_index_name(search_model=search_model)

        def generate_actions():
            queryset = search_model.get_queryset()

            queryset = queryset.filter(pk__in=id_list)

            for instance in queryset:
                kwargs = search_model.populate(
                    search_backend=self, instance=instance
                )
                kwargs['_id'] = kwargs['id']

                yield kwargs

        bulk_indexing_generator = helpers.streaming_bulk(
            client=client, index=index_name, actions=generate_actions(),
            yield_ok=False
        )

        deque(iterable=bulk_indexing_generator, maxlen=0)

    def refresh(self):
        attempt_count = 0
        client = self._get_client()
        search_model_index = 0
        search_models = SearchModel.all()

        while True:
            search_model = search_models[search_model_index]
            index_name = self._get_index_name(search_model=search_model)

            try:
                client.indices.refresh(index=index_name)
            except elasticsearch.exceptions.NotFoundError as exception:
                attempt_count += 1

                if attempt_count > MAXIMUM_API_ATTEMPT_COUNT:
                    raise DynamicSearchBackendException(
                        'Refresh attempt count exceeded the maximum'
                        ' of `{}`.'.format(
                            MAXIMUM_API_ATTEMPT_COUNT
                        )
                    ) from exception
            else:
                attempt_count = 0
                search_model_index += 1
                if search_model_index >= len(search_models):
                    break

    def reset(self, search_model=None):
        self.tear_down(search_model=search_model)
        self._update_mappings(search_model=search_model)

    def tear_down(self, search_model=None):
        client = self._get_client()

        if search_model:
            search_models = (search_model,)
        else:
            search_models = SearchModel.all()

        for search_model in search_models:
            try:
                client.indices.delete(
                    index=self._get_index_name(search_model=search_model)
                )
            except elasticsearch.exceptions.NotFoundError:
                """Ignore non existent indexes."""


BackendQueryType.register(
    klass=BackendQueryTypeExact, search_backend=ElasticSearchBackend
)
BackendQueryType.register(
    klass=BackendQueryFuzzy, search_backend=ElasticSearchBackend
)
BackendQueryType.register(
    klass=BackendQueryTypeGreaterThan, search_backend=ElasticSearchBackend
)
BackendQueryType.register(
    klass=BackendQueryTypeGreaterThanOrEqual,
    search_backend=ElasticSearchBackend
)
BackendQueryType.register(
    klass=BackendQueryTypeLessThan, search_backend=ElasticSearchBackend
)
BackendQueryType.register(
    klass=BackendQueryTypeLessThanOrEqual,
    search_backend=ElasticSearchBackend
)
BackendQueryType.register(
    klass=BackendQueryTypePartial, search_backend=ElasticSearchBackend
)
BackendQueryType.register(
    klass=BackendQueryTypeRange,
    search_backend=ElasticSearchBackend
)
BackendQueryType.register(
    klass=BackendQueryTypeRangeExclusive,
    search_backend=ElasticSearchBackend
)
BackendQueryType.register(
    klass=BackendQueryTypeRegularExpression,
    search_backend=ElasticSearchBackend
)
