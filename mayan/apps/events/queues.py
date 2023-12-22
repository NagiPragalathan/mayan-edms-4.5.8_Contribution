from django.utils.translation import ugettext_lazy as _

from mayan.apps.task_manager.classes import CeleryQueue
from mayan.apps.task_manager.workers import worker_a, worker_c

queue_events_fast = CeleryQueue(
    label=_('Events fast'), name='events_fast', worker=worker_a
)
queue_events_slow = CeleryQueue(
    label=_('Events slow'), name='events_slow', transient=True,
    worker=worker_c
)

queue_events_fast.add_task_type(
    dotted_path='mayan.apps.events.tasks.task_event_commit',
    label=_('Commit an event'), name='task_event_commit'
)

queue_events_slow.add_task_type(
    dotted_path='mayan.apps.events.tasks.task_event_queryset_clear',
    label=_('Clear event querysets'), name='task_event_queryset_clear'
)
queue_events_slow.add_task_type(
    dotted_path='mayan.apps.events.tasks.task_event_queryset_export',
    label=_('Export event querysets'), name='task_event_queryset_export'
)
