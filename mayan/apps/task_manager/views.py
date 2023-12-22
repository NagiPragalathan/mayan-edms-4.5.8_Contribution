from django.http import Http404
from django.utils.translation import ugettext_lazy as _

from mayan.apps.views.generics import SingleObjectListView

from .classes import CeleryQueue, Worker
from .icons import (
    icon_queue_task_type_list, icon_worker_list, icon_worker_queue_list
)
from .permissions import permission_task_view


class QueueTaskTypeListView(SingleObjectListView):
    view_icon = icon_queue_task_type_list
    view_permission = permission_task_view

    def get_extra_context(self):
        queue = self.get_queue()

        return {
            'hide_object': True,
            'object': queue,
            'worker': queue.worker,
            'navigation_object_list': ('worker', 'object'),
            'title': _('Task types for queue: %s') % queue
        }

    def get_queue(self):
        try:
            return CeleryQueue.get(
                queue_name=self.kwargs['queue_name']
            )
        except KeyError:
            raise Http404(
                _('Queue: %s, not found') % self.kwargs['queue_name']
            )

    def get_source_queryset(self):
        return self.get_queue().task_types


class WorkerListView(SingleObjectListView):
    extra_context = {
        'hide_object': True,
        'title': _('Background task workers')
    }
    view_icon = icon_worker_list
    view_permission = permission_task_view

    def get_source_queryset(self):
        return Worker.all()


class WorkerQueueListView(SingleObjectListView):
    view_icon = icon_worker_queue_list
    view_permission = permission_task_view

    def get_extra_context(self):
        return {
            'hide_object': True,
            'object': self.get_worker(),
            'title': _('Queues for worker: %s') % self.get_worker()
        }

    def get_worker(self):
        try:
            return Worker.get(
                name=self.kwargs['worker_name']
            )
        except KeyError:
            raise Http404(
                _('Worker: %s, not found') % self.kwargs['worker_name']
            )

    def get_source_queryset(self):
        return self.get_worker().queues
