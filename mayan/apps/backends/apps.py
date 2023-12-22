from django.utils.translation import ugettext_lazy as _

from mayan.apps.common.apps import MayanAppConfig


class BackendsApp(MayanAppConfig):
    app_namespace = 'backends'
    app_url = 'backends'
    name = 'mayan.apps.backends'
    verbose_name = _('Backends')
