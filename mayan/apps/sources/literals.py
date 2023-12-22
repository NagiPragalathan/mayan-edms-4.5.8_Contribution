from pathlib import Path

from django.conf import settings

DEFAULT_SOURCES_BACKEND_ARGUMENTS = {}

DEFAULT_SOURCES_CACHE_STORAGE_BACKEND = 'django.core.files.storage.FileSystemStorage'
DEFAULT_SOURCES_CACHE_STORAGE_BACKEND_ARGUMENTS = {
    'location': str(
        Path(settings.MEDIA_ROOT, 'source_cache')
    )
}

DEFAULT_SOURCES_LOCK_EXPIRE = 600

SOURCE_ACTION_EXECUTE_TASK_PATH = 'mayan.apps.sources.tasks.task_source_backend_action_execute'

STORAGE_NAME_SOURCE_CACHE_FOLDER = 'sources__source_cache'
