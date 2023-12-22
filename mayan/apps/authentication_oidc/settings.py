from django.utils.translation import ugettext_lazy as _

from mayan.apps.smart_settings.classes import SettingNamespace

from .literals import DEFAULT_AUTHENTICATION_OIDC_USER_PROFILE_URL

namespace = SettingNamespace(
    label=_('Authentication OIDC'), name='authentication_oidc'
)

setting_oidc_user_profile_url = namespace.add_setting(
    default=DEFAULT_AUTHENTICATION_OIDC_USER_PROFILE_URL,
    global_name='AUTHENTICATION_OIDC_USER_PROFILE_URL',
    help_text=_('URL for the OIDC user profile page.')
)
