import datetime
import unicodedata

import dateparser
import dateutil

from django.utils.translation import ugettext_lazy as _

from .exceptions import DynamicSearchValueTransformationError


class ValueTransformation:
    label = None

    def __init__(self, value):
        self.value = value

    def get_label(self):
        return getattr(self, 'label') or self.__class__

    def execute(self):
        try:
            return self._execute()
        except (AttributeError, TypeError, ValueError) as exception:
            """
            Encapsulate conversion exception into a custom exception at the
            last possible moment to avoid hiding local code errors.
            """
            raise DynamicSearchValueTransformationError(
                'Unable apply transformation `{}` to value `{}`.'.format(
                    self.get_label(), self.value
                )
            ) from exception


class ValueTransformationAccentReplace(ValueTransformation):
    label = _('Replace accents')

    def _execute(self):
        if self.value is not None:
            return ''.join(
                letter for letter in unicodedata.normalize('NFD', self.value) if unicodedata.category(letter) != 'Mn'
            )
        else:
            return None


class ValueTransformationAtReplace(ValueTransformation):
    label = _('@ sign replace')

    def _execute(self):
        if self.value is not None:
            return self.value.replace('@', '_at_')
        else:
            return None


class ValueTransformationCasefold(ValueTransformation):
    label = _('Case fold')

    def _execute(self):
        if self.value is not None:
            return self.value.casefold()
        else:
            return None


class ValueTransformationHyphenReplace(ValueTransformation):
    label = _('Hyphen replace')

    def _execute(self):
        if self.value is not None:
            return self.value.replace('-', '_')
        else:
            return None


class ValueTransformationHyphenStrip(ValueTransformation):
    label = _('Hyphen replace')

    def _execute(self):
        if self.value is not None:
            return self.value.replace('-', '')
        else:
            return None


class ValueTransformationToBoolean(ValueTransformation):
    label = _('To boolean')

    def _execute(self):
        if self.value is not None:
            if self.value.lower() == 'true':
                return True
            elif self.value.lower() == 'false':
                return False
            else:
                return None


class ValueTransformationToDateTime(ValueTransformation):
    label = _('To date time')

    def _execute(self):
        if self.value is not None:
            try:
                result = dateutil.parser.parse(
                    default=datetime.datetime(
                        datetime.MINYEAR, 1, 1, 0, 0
                    ), timestr=self.value
                )
                return result.replace(microsecond=0)
            except dateutil.parser.ParserError:
                result = dateparser.parse(date_string=self.value)
                if result is None:
                    raise ValueError
                else:
                    return result.replace(microsecond=0)
        else:
            return None


class ValueTransformationToDateTimeISOFormat(ValueTransformation):
    label = _('Date time ISO format')

    def _execute(self):
        if self.value is not None:
            return self.value.replace(microsecond=0).isoformat()
        else:
            return None


class ValueTransformationToDateTimeSimpleFormat(ValueTransformation):
    label = _('Date time simple format')

    def _execute(self):
        if self.value is not None:
            return self.value.strftime('%Y%m%d%H%M%S')
        else:
            return None


class ValueTransformationToDateTimeTimestamp(ValueTransformation):
    label = _('Date time timestamp format')

    def _execute(self):
        if self.value is not None:
            # ElasticSearch works with decimal seconds for exact match
            # but not for comparison (greater than, etc) matches.
            # Typecasting to integer works for all use cases for all
            # backends.
            return int(self.value.timestamp() * 1000)
        else:
            return None


class ValueTransformationToInteger(ValueTransformation):
    label = _('To integer')

    def _execute(self):
        if self.value is not None:
            return int(self.value)
        else:
            return None


class ValueTransformationToString(ValueTransformation):
    label = _('To string')

    def _execute(self):
        if self.value is not None:
            return str(self.value)
        else:
            return None
