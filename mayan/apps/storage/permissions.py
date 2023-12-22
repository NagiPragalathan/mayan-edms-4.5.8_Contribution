from django.utils.translation import ugettext_lazy as _

from mayan.apps.permissions import PermissionNamespace

namespace = PermissionNamespace(
    label=_('Storage'), name='storage'
)

permission_download_file_delete = namespace.add_permission(
    label=_('Delete user files'), name='download_file_delete'
)
permission_download_file_download = namespace.add_permission(
    label=_('Download user files'), name='download_file_download'
)
permission_download_file_view = namespace.add_permission(
    label=_('View user files'), name='download_file_view'
)
