from django.utils.translation import ugettext_lazy as _

from mayan.apps.common.apps import MayanAppConfig


class SourceWatchFoldersApp(MayanAppConfig):
    app_namespace = 'source_watch_folders'
    app_url = 'source_watch_folders'
    has_tests = True
    name = 'mayan.apps.source_watch_folders'
    verbose_name = _('Watch folders')
