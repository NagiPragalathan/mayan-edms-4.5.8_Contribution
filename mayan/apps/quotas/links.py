from django.utils.translation import ugettext_lazy as _

from mayan.apps.navigation.classes import Link
from mayan.apps.navigation.utils import factory_condition_queryset_access

from .icons import (
    icon_quota_create, icon_quota_delete, icon_quota_edit, icon_quota_list,
    icon_quota_setup
)
from .permissions import (
    permission_quota_create, permission_quota_delete,
    permission_quota_edit, permission_quota_view,
)

link_quota_create = Link(
    icon=icon_quota_create, permissions=(permission_quota_create,),
    text=_('Create quota'), view='quotas:quota_backend_selection'
)
link_quota_delete = Link(
    args='resolved_object.pk', icon=icon_quota_delete,
    permissions=(permission_quota_delete,), tags='dangerous',
    text=_('Delete'), view='quotas:quota_delete'
)
link_quota_edit = Link(
    args='object.pk', icon=icon_quota_edit,
    permissions=(permission_quota_edit,), text=_('Edit'),
    view='quotas:quota_edit'
)
link_quota_list = Link(
    icon=icon_quota_list, text=_('Quotas list'), view='quotas:quota_list'
)
link_quota_setup = Link(
    condition=factory_condition_queryset_access(
        app_label='quotas', model_name='Quota',
        object_permission=permission_quota_view,
        view_permission=permission_quota_create,
    ), icon=icon_quota_setup, text=_('Quotas'),
    view='quotas:quota_list'
)
