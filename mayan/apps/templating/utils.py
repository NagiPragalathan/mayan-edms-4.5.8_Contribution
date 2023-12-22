import re

from django.template import TemplateSyntaxError


def process_regex_flags(**kwargs):
    result = 0

    REGEX_FLAGS = {
        'ascii': re.ASCII,
        'ignorecase': re.IGNORECASE,
        'locale': re.LOCALE,
        'multiline': re.MULTILINE,
        'dotall': re.DOTALL,
        'verbose': re.VERBOSE
    }

    for key, value in kwargs.items():
        if value is True:
            try:
                result = result | REGEX_FLAGS[key]
            except KeyError:
                raise TemplateSyntaxError(
                    'Unknown or unsupported regular expression '
                    'flag: "{}"'.format(key)
                )

    return result
