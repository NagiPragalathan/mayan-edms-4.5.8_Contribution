from django.utils.translation import ugettext_lazy as _

COMMAND_NAME_SEARCH_INDEX_OBJECTS = 'search_index_objects'
COMMAND_NAME_SEARCH_REINDEX = 'search_reindex'
COMMAND_NAME_SEARCH_STATUS = 'search_status'

DEFAULT_SEARCH_BACKEND = 'mayan.apps.dynamic_search.backends.whoosh.WhooshSearchBackend'
DEFAULT_SEARCH_BACKEND_ARGUMENTS = {}
DEFAULT_SEARCH_DISABLE_SIMPLE_SEARCH = False
DEFAULT_SEARCH_INDEXING_CHUNK_SIZE = 25
DEFAULT_SEARCH_MATCH_ALL_DEFAULT_VALUE = 'False'
DEFAULT_SEARCH_QUERY_RESULTS_LIMIT = 100000
DEFAULT_SEARCH_RESULTS_LIMIT = 1000
DEFAULT_TEST_SEARCH_BACKEND = 'mayan.apps.dynamic_search.backends.django.DjangoSearchBackend'

ERROR_TEXT_NO_RESULT_SCOPE = 'No result scope has been specified.'

FILTER_PREFIX = 'filter_'

MATCH_ALL_FIELD_CHOICES = (
    (True, _('Yes')),
    (False, _('No'))
)
MATCH_ALL_FIELD_NAME = '_match_all'
MATCH_ALL_VALUES = ('on', 'true', 'yes')
MESSAGE_FEATURE_NO_STATUS = 'This backend does not provide status information.'

QUERY_PARAMETER_ANY_FIELD = 'q'

SCOPE_DELIMITER = '_'
SCOPE_MARKER = '__'
SCOPE_RESULT_MARKER = 'result'

SCOPE_OPERATOR_AND = 'AND'
SCOPE_OPERATOR_NOT = 'NOT'
SCOPE_OPERATOR_OR = 'OR'


def scope_operation_and(*args):
    result = set(args[0])
    for argument in args[1:]:
        result = result.intersection(argument)

    return result


def scope_operation_not(*args):
    result = set(args[0])
    for argument in args[1:]:
        result = result.difference(argument)

    return result


def scope_operation_or(*args):
    result = set(args[0])
    for argument in args[1:]:
        result = result.union(argument)

    return result


SCOPE_OPERATOR_CHOICES = {
    SCOPE_OPERATOR_AND: scope_operation_and,
    SCOPE_OPERATOR_NOT: scope_operation_not,
    SCOPE_OPERATOR_OR: scope_operation_or
}

DEFAULT_SEARCH_DEFAULT_OPERATOR = SCOPE_OPERATOR_AND

SEARCH_MODEL_NAME_KWARG = 'search_model_pk'

TASK_DEINDEX_INSTANCE_MAX_RETRIES = 40
TASK_DEINDEX_INSTANCE_RETRY_BACKOFF_MAX = 60

TASK_INDEX_INSTANCE_MAX_RETRIES = 40
TASK_INDEX_INSTANCE_RETRY_BACKOFF_MAX = 60

TASK_INDEX_INSTANCES_MAX_RETRIES = 40
TASK_INDEX_INSTANCES_RETRY_BACKOFF_MAX = 60

TASK_INDEX_RELATED_INSTANCE_M2M_MAX_RETRIES = 40
TASK_INDEX_RELATED_INSTANCE_M2M_RETRY_BACKOFF_MAX = 60

TERM_OPERATOR_AND = 'AND'
TERM_OPERATOR_NOT = 'NOT'
TERM_OPERATOR_OR = 'OR'
TERM_OPERATORS = [
    TERM_OPERATOR_AND, TERM_OPERATOR_NOT, TERM_OPERATOR_OR
]

TERM_MARKER_QUOTE = '"'
TERM_MARKER_RAW = '`'
TERM_MARKER_SPACE_CHARACTER = ' '
