from django.utils.translation import ugettext_lazy as _

from mayan.apps.task_manager.classes import CeleryQueue
from mayan.apps.task_manager.workers import worker_b, worker_c

queue_indexing = CeleryQueue(
    label=_('Indexing'), name='indexing', worker=worker_b
)
queue_indexing_slow = CeleryQueue(
    label=_('Indexing slow'), name='indexing_slow', worker=worker_c
)

queue_indexing.add_task_type(
    label=_('Remove document'),
    dotted_path='mayan.apps.document_indexing.tasks.task_index_instance_document_remove'
)
queue_indexing.add_task_type(
    label=_('Index document'),
    dotted_path='mayan.apps.document_indexing.tasks.task_index_instance_document_add'
)

queue_indexing_slow.add_task_type(
    label=_('Rebuild index'),
    dotted_path='mayan.apps.document_indexing.tasks.task_index_template_rebuild'
)
