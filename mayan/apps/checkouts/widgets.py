import datetime

from django import forms
from django.utils.timezone import now
from django.utils.translation import ugettext_lazy as _

from mayan.apps.common.literals import TIME_DELTA_UNIT_CHOICES
from mayan.apps.views.widgets import NamedMultiWidget


class SplitTimeDeltaWidget(NamedMultiWidget):
    """
    A Widget that splits a timedelta input into two field: one for unit of
    time and another for the amount of units.
    """
    subwidgets = {
        'amount': forms.widgets.NumberInput(
            attrs={
                'maxlength': 4, 'style': 'width: 8em;',
                'placeholder': _('Amount')
            }
        ),
        'unit': forms.widgets.Select(
            attrs={'style': 'width: 8em;'}, choices=TIME_DELTA_UNIT_CHOICES
        )
    }

    def decompress(self, value):
        return {
            'amount': None, 'unit': None
        }

    def value_from_datadict(self, querydict, files, name):
        amount = querydict.get(
            '{}_amount'.format(name)
        )
        unit = querydict.get(
            '{}_unit'.format(name)
        )

        if not unit or not amount:
            return now()

        amount = int(amount)

        timedelta = datetime.timedelta(
            **{unit: amount}
        )
        return now() + timedelta
