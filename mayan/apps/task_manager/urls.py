from django.conf.urls import url

from .views import (
    QueueTaskTypeListView, WorkerListView, WorkerQueueListView
)

urlpatterns = [
    url(
        regex=r'^queues/(?P<queue_name>\w+)/task_types/$',
        view=QueueTaskTypeListView.as_view(), name='queue_task_type_list'
    ),
    url(
        regex=r'^workers/$', view=WorkerListView.as_view(),
        name='worker_list'
    ),
    url(
        regex=r'^workers/(?P<worker_name>\w+)/queues/$',
        view=WorkerQueueListView.as_view(), name='worker_queue_list'
    )
]
