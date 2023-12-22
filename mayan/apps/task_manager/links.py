from django.utils.translation import ugettext_lazy as _

from mayan.apps.navigation.classes import Link

from .icons import (
    icon_queue_task_type_list, icon_worker_list, icon_worker_queue_list
)
from .permissions import permission_task_view


link_queue_task_type_list = Link(
    icon=icon_queue_task_type_list, kwargs={
        'queue_name': 'resolved_object.name'
    }, permissions=(permission_task_view,), text=_('Task type list'),
    view='task_manager:queue_task_type_list'
)
link_worker_list = Link(
    icon=icon_worker_list, permissions=(permission_task_view,),
    text=_('Worker list'), view='task_manager:worker_list'
)
link_worker_queue_list = Link(
    icon=icon_worker_queue_list, kwargs={
        'worker_name': 'resolved_object.name'
    }, permissions=(permission_task_view,), text=_('Queue list'),
    view='task_manager:worker_queue_list'
)
