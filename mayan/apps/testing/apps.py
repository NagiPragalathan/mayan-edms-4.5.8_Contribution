from django.core import checks
import django.test.runner
from django.utils.translation import ugettext_lazy as _

from mayan.apps.common.apps import MayanAppConfig

from .checks import check_app_tests
from .runner import filter_tests_by_tags


class TestingApp(MayanAppConfig):
    name = 'mayan.apps.testing'
    verbose_name = _('Testing')

    def ready(self, *args, **kwargs):
        super().ready(*args, **kwargs)

        checks.register(check=check_app_tests)

        # Replace Django's implementation with the enhanced version.
        setattr(
            django.test.runner, 'filter_tests_by_tags', filter_tests_by_tags
        )
