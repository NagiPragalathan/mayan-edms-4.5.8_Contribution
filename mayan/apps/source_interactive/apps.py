from django.utils.translation import ugettext_lazy as _

from mayan.apps.common.apps import MayanAppConfig


class SourceInteractiveApp(MayanAppConfig):
    app_namespace = 'source_interactive'
    app_url = 'source_interactive'
    has_tests = True
    name = 'mayan.apps.source_interactive'
    verbose_name = _('Source interactive')
