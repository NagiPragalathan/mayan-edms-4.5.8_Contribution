from pathlib import Path
import os
import sys

from django.core.exceptions import ImproperlyConfigured
from django.utils.translation import ugettext_lazy as _

from mayan.apps.smart_settings.literals import COMMAND_NAME_SETTINGS_REVERT
from mayan.apps.smart_settings.utils import SettingNamespaceSingleton

from .literals import DEFAULT_SECRET_KEY, SECRET_KEY_FILENAME, SYSTEM_DIR

BASE_DIR = Path(__file__).parent.parent
# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/3.2/howto/deployment/checklist/

setting_namespace = SettingNamespaceSingleton(
    global_symbol_table=globals()
)

if COMMAND_NAME_SETTINGS_REVERT in sys.argv:
    setting_namespace.update_globals(only_critical=True)
    DATABASES = {
        'default': {
            'ENGINE': 'django.db.backends.sqlite3',
            'NAME': Path(MEDIA_ROOT, 'db.sqlite3')  # NOQA: F821
        }
    }
else:
    setting_namespace.update_globals()

try:
    SECRET_KEY = os.environ['MAYAN_SECRET_KEY']
except KeyError:
    path_secret_key = Path(
        MEDIA_ROOT, SYSTEM_DIR, SECRET_KEY_FILENAME  # NOQA: F821
    )
    try:
        with path_secret_key.open(mode='rb') as file_object:  # NOQA: F821
            SECRET_KEY = file_object.read().strip()
    except FileNotFoundError:
        SECRET_KEY = DEFAULT_SECRET_KEY

# Application definition

INSTALLED_APPS = (
    # Placed at the top so it can preload all events defined by apps.
    'mayan.apps.events',
    # Placed at the top so it can override any template.
    'mayan.apps.appearance',
    # Django
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.messages',
    'django.contrib.sessions',
    'django.contrib.sites',
    'django.forms',
    'django.contrib.staticfiles',
    # 3rd party.
    'actstream',
    'corsheaders',
    'django_celery_beat',
    'formtools',
    'mathfilters',
    'mozilla_django_oidc',
    'mptt',
    'rest_framework',
    'rest_framework.authtoken',
    'solo',
    'stronghold',
    'widget_tweaks',
    # Base apps
    # Moved to the top to ensure Mayan app logging is initialized and
    # available as soon as possible.
    'mayan.apps.logging',
    # Task manager goes to the top to ensure all queues are created before any
    # other app tries to use them.
    'mayan.apps.task_manager',
    'mayan.apps.acls',
    # User management app must go before authentication to ensure the Group
    # and User models are properly setup using runtime methods.
    'mayan.apps.user_management',
    'mayan.apps.authentication',
    'mayan.apps.authentication_oidc',
    'mayan.apps.authentication_otp',
    'mayan.apps.autoadmin',
    'mayan.apps.backends',
    'mayan.apps.common',
    'mayan.apps.converter',
    'mayan.apps.credentials',
    'mayan.apps.dashboards',
    'mayan.apps.databases',
    'mayan.apps.dependencies',
    'mayan.apps.django_gpg',
    'mayan.apps.dynamic_search',
    'mayan.apps.file_caching',
    'mayan.apps.locales',
    'mayan.apps.lock_manager',
    'mayan.apps.messaging',
    'mayan.apps.mime_types',
    'mayan.apps.navigation',
    'mayan.apps.organizations',
    'mayan.apps.permissions',
    'mayan.apps.platform',
    'mayan.apps.quotas',
    'mayan.apps.rest_api',
    'mayan.apps.smart_settings',
    'mayan.apps.storage',
    'mayan.apps.templating',
    'mayan.apps.testing',
    'mayan.apps.views',
    'mayan.apps.announcements',
    # Obsolete apps. Need to remain to allow migrations to execute.
    'mayan.apps.motd',
    # Document apps.
    'mayan.apps.cabinets',
    'mayan.apps.checkouts',
    'mayan.apps.document_comments',
    'mayan.apps.document_downloads',
    'mayan.apps.document_exports',
    'mayan.apps.document_indexing',
    'mayan.apps.document_parsing',
    'mayan.apps.document_signatures',
    'mayan.apps.document_states',
    'mayan.apps.documents',
    'mayan.apps.duplicates',
    'mayan.apps.file_metadata',
    'mayan.apps.linking',
    'mayan.apps.mailer',
    'mayan.apps.mayan_statistics',
    'mayan.apps.metadata',
    'mayan.apps.mirroring',
    'mayan.apps.ocr',
    'mayan.apps.redactions',
    'mayan.apps.signature_captures',
    'mayan.apps.source_compressed',
    'mayan.apps.source_interactive',
    'mayan.apps.source_periodic',
    'mayan.apps.source_emails',
    'mayan.apps.source_sane_scanners',
    'mayan.apps.source_staging_folders',
    'mayan.apps.source_staging_storages',
    'mayan.apps.source_generated_files',
    'mayan.apps.source_stored_files',
    'mayan.apps.source_watch_folders',
    'mayan.apps.source_watch_storages',
    'mayan.apps.source_web_forms',
    'mayan.apps.sources',
    'mayan.apps.tags',
    'mayan.apps.web_links',
    # Placed after rest_api to allow template overriding.
    'drf_yasg',
)

MIDDLEWARE = (
    'mayan.apps.logging.middleware.error_logging.ErrorLoggingMiddleware',
    'django.middleware.security.SecurityMiddleware',
    'whitenoise.middleware.WhiteNoiseMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.locale.LocaleMiddleware',
    'corsheaders.middleware.CorsMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'mayan.apps.locales.middleware.locales.UserLocaleProfileMiddleware',
    'mayan.apps.authentication.middleware.impersonate.ImpersonateMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
    'stronghold.middleware.LoginRequiredMiddleware',
    'mayan.apps.views.middleware.ajax_redirect.AjaxRedirect'
)

ROOT_URLCONF = 'mayan.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [],
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.i18n',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages'
            ],
            'loaders': [
                'django.template.loaders.filesystem.Loader',
                'django.template.loaders.app_directories.Loader'
            ]
        }
    }
]

WSGI_APPLICATION = 'mayan.wsgi.application'

# Password validation
# https://docs.djangoproject.com/en/3.2/ref/settings/#auth-password-validators

AUTH_PASSWORD_VALIDATORS = [
    {
        'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator'
    },
    {
        'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator'
    },
    {
        'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator'
    },
    {
        'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator'
    }
]

# Internationalization
# https://docs.djangoproject.com/en/3.2/topics/i18n/

LANGUAGE_CODE = 'en-us'

TIME_ZONE = 'UTC'

USE_I18N = True

USE_L10N = True

USE_TZ = True

# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/3.2/howto/static-files/

STATIC_URL = '/static/'

# ------------ Custom settings section ----------

LANGUAGES = (
    ('ar-eg', _('Arabic (Egypt)')),
    ('ar', _('Arabic')),
    ('bg', _('Bulgarian')),
    ('bs', _('Bosnian')),
    ('ca', _('Catalan')),
    ('cs', _('Czech')),
    ('da', _('Danish')),
    ('de-at', _('German (Austria)')),
    ('de-de', _('German (Germany)')),
    ('el', _('Greek')),
    ('en', _('English')),
    ('es', _('Spanish')),
    ('es-mx', _('Spanish (Mexico)')),
    ('es-pr', _('Spanish (Puerto Rico)')),
    ('fa', _('Persian')),
    ('fr', _('French')),
    ('he-il', _('Hebrew (Israel)')),
    ('hu', _('Hungarian')),
    ('hr', _('Croatian')),
    ('id', _('Indonesian')),
    ('it', _('Italian')),
    ('lv', _('Latvian')),
    ('mn-mn', _('Mongolian (Mongolia)')),
    ('nl', _('Dutch')),
    ('pl', _('Polish')),
    ('pt', _('Portuguese')),
    ('pt-br', _('Portuguese (Brazil)')),
    ('ro-ro', _('Romanian (Romania)')),
    ('ru', _('Russian')),
    ('sl', _('Slovenian')),
    ('sq', _('Albanian')),
    ('th', _('Thai')),
    ('tr', _('Turkish')),
    ('tr-tr', _('Turkish (Turkey)')),
    ('uk', _('Ukrainian')),
    ('vi', _('Vietnamese')),
    ('zh-cn', _('Chinese (China)')),
    ('zh-hans', _('Chinese (Simplified)')),
    ('zh-tw', _('Chinese (Taiwan)'))
)

MEDIA_URL = 'media/'

SITE_ID = 1

STATIC_ROOT = os.environ.get(
    'MAYAN_STATIC_ROOT', Path(MEDIA_ROOT, 'static')  # NOQA: F821
)

MEDIA_URL = 'media/'

# Silence warning and keep default for the time being.
# https://docs.djangoproject.com/en/3.2/releases/3.2/#customizing-type-of-auto-created-primary-keys
DEFAULT_AUTO_FIELD = 'django.db.models.AutoField'

STATICFILES_FINDERS = (
    'django.contrib.staticfiles.finders.FileSystemFinder',
    'mayan.apps.views.finders.MayanAppDirectoriesFinder'
)

STATICFILES_STORAGE = 'whitenoise.storage.CompressedManifestStaticFilesStorage'

TEST_RUNNER = 'mayan.apps.testing.runner.MayanTestRunner'

# ---------- Django REST framework -----------

REST_FRAMEWORK = {
    'DEFAULT_AUTHENTICATION_CLASSES': (
        'rest_framework.authentication.SessionAuthentication',
        'rest_framework.authentication.TokenAuthentication',
        'rest_framework.authentication.BasicAuthentication'
    ),
    'DEFAULT_PAGINATION_CLASS': 'mayan.apps.rest_api.pagination.MayanPageNumberPagination',
    'EXCEPTION_HANDLER': 'mayan.apps.rest_api.exception_handlers.mayan_exception_handler'
}

# --------- Pagination --------

PAGINATION_SETTINGS = {
    'PAGE_RANGE_DISPLAYED': 5,
    'MARGIN_PAGES_DISPLAYED': 2
}

# ----------- Celery ----------

CELERY_ACCEPT_CONTENT = ('json',)
CELERY_BEAT_SCHEDULE = {}
CELERY_BEAT_SCHEDULER = 'django_celery_beat.schedulers.DatabaseScheduler'
CELERY_DISABLE_RATE_LIMITS = True
CELERY_ENABLE_UTC = True
CELERY_RESULT_SERIALIZER = 'json'
CELERY_TASK_ALWAYS_EAGER = False
CELERY_TASK_CREATE_MISSING_QUEUES = True
CELERY_TASK_DEFAULT_QUEUE = 'celery'
CELERY_TASK_EAGER_PROPAGATES = True
CELERY_TASK_QUEUES = []
CELERY_TASK_ROUTES = {}
CELERY_TASK_SERIALIZER = 'json'
CELERY_TIMEZONE = 'UTC'

# ------------ CORS ------------

CORS_ORIGIN_ALLOW_ALL = True

# ------ Timezone --------

TIMEZONE_COOKIE_NAME = 'django_timezone'
TIMEZONE_SESSION_KEY = 'django_timezone'

# ----- Stronghold -------

STRONGHOLD_PUBLIC_URLS = (r'^/favicon\.ico$',)

# ----- Swagger --------

SWAGGER_SETTINGS = {
    'DEFAULT_INFO': 'rest_api.schemas.openapi_info',
    'DEFAULT_MODEL_DEPTH': 1,
    'DOC_EXPANSION': 'None'
}

# ------ End -----

BASE_INSTALLED_APPS = INSTALLED_APPS

for app in INSTALLED_APPS:
    if 'mayan.apps.{}'.format(app) in BASE_INSTALLED_APPS:
        raise ImproperlyConfigured(
            'Update the app references in the file config.yml as detailed '
            'in https://docs.mayan-edms.com/releases/3.2.html#backward-incompatible-changes'
        )

repeated_apps = tuple(
    set(COMMON_EXTRA_APPS_PRE).intersection(  # NOQA: F821
        set(COMMON_EXTRA_APPS)  # NOQA: F821
    )
)
if repeated_apps:
    raise ImproperlyConfigured(
        'Apps "{}" cannot be specified in `COMMON_EXTRA_APPS_PRE` and '
        '`COMMON_EXTRA_APPS` at the same time.'.format(
            ', '.join(
                tuple(repeated_apps)
            )
        )
    )

INSTALLED_APPS = tuple(
    COMMON_EXTRA_APPS_PRE or ()  # NOQA: F821
) + INSTALLED_APPS

INSTALLED_APPS = INSTALLED_APPS + tuple(
    COMMON_EXTRA_APPS or ()  # NOQA: F821
)

INSTALLED_APPS = [
    APP for APP in INSTALLED_APPS if APP not in (
        COMMON_DISABLED_APPS or ()  # NOQA: F821
    )
]

if not DATABASES:
    if DATABASE_ENGINE:  # NOQA: F821
        DATABASES = {
            'default': {
                'ENGINE': DATABASE_ENGINE,  # NOQA: F821
                'NAME': DATABASE_NAME,  # NOQA: F821
                'USER': DATABASE_USER,  # NOQA: F821
                'PASSWORD': DATABASE_PASSWORD,  # NOQA: F821
                'HOST': DATABASE_HOST,  # NOQA: F821
                'PORT': DATABASE_PORT,  # NOQA: F821
                'CONN_MAX_AGE': DATABASE_CONN_MAX_AGE  # NOQA: F821
            }
        }
    else:
        DATABASES = {
            'default': {
                'ENGINE': 'django.db.backends.sqlite3',
                'NAME': str(
                    Path(MEDIA_ROOT, 'db.sqlite3')  # NOQA: F821
                )
            }
        }
