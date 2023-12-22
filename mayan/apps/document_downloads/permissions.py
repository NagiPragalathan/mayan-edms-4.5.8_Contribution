from django.utils.translation import ugettext_lazy as _

from mayan.apps.permissions import PermissionNamespace

namespace = PermissionNamespace(
    label=_('Document downloads'), name='document_downloads'
)

permission_document_file_download = namespace.add_permission(
    label=_('Download document files'),
    name='document_file_download'
)
