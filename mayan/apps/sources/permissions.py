from django.utils.translation import ugettext_lazy as _

from mayan.apps.permissions import PermissionNamespace

namespace = PermissionNamespace(
    label=_('Sources setup'), name='sources_setup'
)

# Documents

permission_sources_metadata_view = namespace.add_permission(
    label=_('View document source metadata'), name='source_metadata_view'
)

# Sources

permission_sources_create = namespace.add_permission(
    label=_('Create new document sources'), name='sources_setup_create'
)
permission_sources_delete = namespace.add_permission(
    label=_('Delete document sources'), name='sources_setup_delete'
)
permission_sources_edit = namespace.add_permission(
    label=_('Edit document sources'), name='sources_setup_edit'
)
permission_sources_view = namespace.add_permission(
    label=_('View existing document sources'), name='sources_setup_view'
)
