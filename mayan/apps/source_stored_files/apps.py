from django.utils.translation import ugettext_lazy as _

from mayan.apps.common.apps import MayanAppConfig


class SourceStoredFileApp(MayanAppConfig):
    app_namespace = 'source_stored_files'
    app_url = 'source_stored_files'
    has_tests = True
    name = 'mayan.apps.source_stored_files'
    verbose_name = _('Source stored files')
