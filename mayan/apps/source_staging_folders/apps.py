from django.utils.translation import ugettext_lazy as _

from mayan.apps.common.apps import MayanAppConfig


class SourceStagingFoldersApp(MayanAppConfig):
    app_namespace = 'source_staging_folders'
    app_url = 'source_staging_folders'
    has_rest_api = False
    has_static_media = False
    has_tests = True
    name = 'mayan.apps.source_staging_folders'
    verbose_name = _('Staging folders')
