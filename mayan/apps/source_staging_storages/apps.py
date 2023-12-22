from django.utils.translation import ugettext_lazy as _

from mayan.apps.common.apps import MayanAppConfig


class SourceStagingStorageApp(MayanAppConfig):
    app_namespace = 'source_staging_storages'
    app_url = 'source_staging_storages'
    has_rest_api = False
    has_static_media = False
    has_tests = True
    name = 'mayan.apps.source_staging_storages'
    verbose_name = _('Staging storages')
