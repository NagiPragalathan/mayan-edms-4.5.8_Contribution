from django.template import Library

from ..tests.literals import TEST_TEMPLATE_TAG_RESULT

register = Library()


@register.simple_tag
def templating_test_tag():
    return TEST_TEMPLATE_TAG_RESULT
