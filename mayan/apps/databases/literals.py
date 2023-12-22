from django.utils.translation import ugettext_lazy as _

DATABASE_MINIMUM_ID = 1

DJANGO_POSITIVE_INTEGER_FIELD_MAX_VALUE = 2147483647

DJANGO_SQLITE_BACKEND = 'django.db.backends.sqlite3'

MESSAGE_SQLITE_WARNING = _(
    'Your database backend is set to use SQLite. SQLite should only be used '
    'for development and testing, not for production.'
)
