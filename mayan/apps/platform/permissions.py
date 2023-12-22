from django.utils.translation import ugettext_lazy as _

from mayan.apps.permissions import PermissionNamespace

namespace = PermissionNamespace(
    label=_('Platform'), name='platform'
)

permission_test_trigger = namespace.add_permission(
    label=_('Trigger tests'), name='trigger_tests'
)
