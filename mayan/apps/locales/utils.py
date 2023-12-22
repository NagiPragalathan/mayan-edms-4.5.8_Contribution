from pytz import common_timezones

from django.conf import settings
from django.utils import translation


def get_language_choices():
    return sorted(
        settings.LANGUAGES, key=lambda entry: entry[1]
    )


def to_language(promise, language):
    current_language = translation.get_language()
    translation.activate(language=language)
    result = str(promise)
    translation.activate(language=current_language)

    return result


def get_timezone_choices():
    return zip(common_timezones, common_timezones)
