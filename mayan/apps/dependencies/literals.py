from django.utils.translation import ugettext_lazy as _

COMMAND_NAME_DEPENDENCIES_CHECK_VERSION = 'dependencies_check_version'
COMMAND_NAME_DEPENDENCIES_INSTALL = 'dependencies_install'
COMMAND_NAME_DEPENDENCIES_SHOW_VERSION = 'dependencies_show_version'

MAYAN_PYPI_NAME = 'mayan-edms'

MESSAGE_GREATER_THAN_SERVER = _(
    'Your version (%(version_local)s), is more recent than the published '
    'version (%(version_server)s).'
)
MESSAGE_NOT_LATEST = _(
    'The version you are using (%(version_local)s) is '
    'outdated. The latest version is %(version_server)s.'
)
MESSAGE_UNKNOWN_VERSION = _(
    'It is not possible to determine the latest version available.'
)
MESSAGE_UNEXPECTED_ERROR = _(
    'Unexpected error trying to determine the latest version available. '
    'Make sure your installation has a connection to the internet; '
    '%(exception)s'
)
MESSAGE_UP_TO_DATE = 'Your version (%(version_local)s), is up-to-date.'

PYPI_URL = 'https://pypi.org'
