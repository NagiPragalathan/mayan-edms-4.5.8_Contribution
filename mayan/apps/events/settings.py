from django.utils.translation import ugettext_lazy as _

from mayan.apps.smart_settings.classes import SettingNamespace

from .literals import DEFAULT_EVENTS_DISABLE_ASYNCHRONOUS_MODE

namespace = SettingNamespace(label=_('Events'), name='events')

setting_disable_asynchronous_mode = namespace.add_setting(
    default=DEFAULT_EVENTS_DISABLE_ASYNCHRONOUS_MODE,
    global_name='EVENTS_DISABLE_ASYNCHRONOUS_MODE',
    help_text=_(
        'Disables asynchronous events mode. All events will be committed '
        'in the same process that triggers them. This was the behavior '
        'prior to version 4.5.'
    )
)
