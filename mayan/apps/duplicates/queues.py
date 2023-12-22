from django.utils.translation import ugettext_lazy as _

from mayan.apps.task_manager.classes import CeleryQueue
from mayan.apps.task_manager.workers import worker_c

queue_duplicates = CeleryQueue(
    label=_('Duplicates'), name='duplicates', worker=worker_c
)
queue_duplicates_slow = CeleryQueue(
    label=_('Duplicates slow'), name='duplicates_slow', worker=worker_c
)

queue_duplicates.add_task_type(
    dotted_path='mayan.apps.duplicates.tasks.task_duplicates_clean_empty_lists',
    label=_('Clean empty duplicate lists')
)
queue_duplicates.add_task_type(
    dotted_path='mayan.apps.duplicates.tasks.task_duplicates_scan_for',
    label=_('Scan document duplicates')
)

queue_duplicates_slow.add_task_type(
    dotted_path='mayan.apps.duplicates.tasks.task_duplicates_scan_all',
    label=_('Duplicated document scan')
)
