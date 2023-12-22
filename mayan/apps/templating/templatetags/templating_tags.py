from datetime import timedelta
import re

from dateutil.parser import parse

from django.template import Library, Node, TemplateSyntaxError
from django.utils.html import strip_spaces_between_tags

from ..utils import process_regex_flags

register = Library()


@register.filter
def date_parse(date_string):
    """
    Takes a string and converts it into a datetime object.
    """
    return parse(timestr=date_string)


@register.filter
def dict_get(dictionary, key):
    """
    Return the value for the given key or '' if not found.
    """
    return dictionary.get(key, '')


@register.simple_tag
def method(obj, method, *args, **kwargs):
    """
    Call an object method. {% method object method **kwargs %}
    """
    try:
        return getattr(obj, method)(*args, **kwargs)
    except Exception as exception:
        raise TemplateSyntaxError(
            'Error calling object method; {}'.format(exception)
        )


@register.simple_tag
def regex_findall(pattern, string, **kwargs):
    """
    Return all non-overlapping matches of pattern in string, as a list of
    strings. {% regex_findall pattern string flags %}
    """
    flags = process_regex_flags(**kwargs)
    return re.findall(flags=flags, pattern=pattern, string=string)


@register.simple_tag
def regex_match(pattern, string, **kwargs):
    """
    If zero or more characters at the beginning of string match the regular
    expression pattern, return a corresponding match object.
    {% regex_match pattern string flags %}
    """
    flags = process_regex_flags(**kwargs)
    return re.match(flags=flags, pattern=pattern, string=string)


@register.simple_tag
def regex_search(pattern, string, **kwargs):
    """
    Scan through string looking for the first location where the regular
    expression pattern produces a match, and return a corresponding
    match object. {% regex_search pattern string flags %}
    """
    flags = process_regex_flags(**kwargs)
    return re.search(flags=flags, pattern=pattern, string=string)


@register.simple_tag
def regex_sub(pattern, repl, string, count=0, **kwargs):
    """
    Replacing the leftmost non-overlapping occurrences of pattern in
    string with repl. {% regex_sub pattern repl string count=0 flags %}
    """
    flags = process_regex_flags(**kwargs)
    return re.sub(
        count=count, flags=flags, pattern=pattern, repl=repl, string=string
    )


@register.simple_tag
def set(value):
    """
    Set a context variable to a specific value.
    """
    return value


@register.filter
def split(obj, separator):
    """
    Return a list of the words in the string, using sep as the delimiter
    string.
    """
    return obj.split(separator)


class SpacelessPlusNode(Node):
    def __init__(self, nodelist):
        self.nodelist = nodelist

    def render(self, context):
        content = self.nodelist.render(context).strip()
        result = []
        for line in content.split('\n'):
            if line.strip() != '':
                result.append(line)

        return strip_spaces_between_tags(
            value='\n'.join(result)
        )


@register.tag
def spaceless_plus(parser, token):
    """
    Removes empty lines between the tag nodes.
    """
    nodelist = parser.parse(
        ('endspaceless_plus',)
    )
    parser.delete_first_token()
    return SpacelessPlusNode(nodelist=nodelist)


@register.simple_tag(name='timedelta')
def tag_timedelta(date, **kwargs):
    """
    Takes a datetime object and applies a timedelta.
    """
    return date + timedelta(**kwargs)
