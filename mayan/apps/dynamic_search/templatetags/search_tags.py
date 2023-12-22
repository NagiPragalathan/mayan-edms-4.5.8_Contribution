from django.template import Library

from ..literals import (
    FILTER_PREFIX, SEARCH_MODEL_NAME_KWARG, QUERY_PARAMETER_ANY_FIELD
)
from ..search_models import SearchModel

register = Library()


@register.simple_tag
def search_get_default_search_model():
    return SearchModel.get_default()


@register.simple_tag
def search_get_filter_prefix():
    return FILTER_PREFIX


@register.simple_tag
def search_get_query_any_field_value(query=None):
    query = query or {}
    return query.get(QUERY_PARAMETER_ANY_FIELD, '')


@register.simple_tag
def search_get_query_parameter_any_field():
    return QUERY_PARAMETER_ANY_FIELD


@register.simple_tag
def search_get_search_models():
    return SearchModel.all()


@register.simple_tag
def search_get_search_model_name_query_variable():
    return '_{}'.format(SEARCH_MODEL_NAME_KWARG)
