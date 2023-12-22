from django.utils.translation import ugettext_lazy as _

from mayan.apps.permissions import PermissionNamespace

namespace = PermissionNamespace(
    label=_('Document exports'), name='document_exports'
)

permission_document_version_export = namespace.add_permission(
    label=_('Export document versions'),
    name='document_version_export'
)
