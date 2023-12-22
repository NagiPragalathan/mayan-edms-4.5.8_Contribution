from datetime import timedelta

from django.utils.translation import ugettext_lazy as _

from mayan.apps.task_manager.classes import CeleryQueue
from mayan.apps.task_manager.workers import worker_b, worker_c

from .literals import (
    CHECK_DELETE_PERIOD_INTERVAL, CHECK_TRASH_PERIOD_INTERVAL,
    INTERVAL_TASK_STUBS_DELETION
)

queue_documents_fast = CeleryQueue(
    name='documents_fast', label=_('Documents fast'), worker=worker_b
)
queue_documents_file = CeleryQueue(
    name='documents_file', label=_('Documents file'), worker=worker_b
)
queue_documents_file_slow = CeleryQueue(
    name='documents_file_slow', label=_('Documents file slow'),
    worker=worker_b
)
queue_documents_periodic = CeleryQueue(
    name='documents_periodic', label=_('Documents periodic'), transient=True,
    worker=worker_c
)
queue_documents_trash = CeleryQueue(
    name='documents_trash', label=_('Documents trash'), worker=worker_c
)
queue_documents_version = CeleryQueue(
    name='documents_version', label=_('Documents version'), worker=worker_b
)

queue_documents_fast.add_task_type(
    dotted_path='mayan.apps.documents.tasks.document_file_tasks.task_document_file_create',
    label=_('Create new document file')
)
queue_documents_fast.add_task_type(
    dotted_path='mayan.apps.documents.tasks.document_file_tasks.task_document_file_upload',
    label=_('Upload new document file')
)
queue_documents_fast.add_task_type(
    dotted_path='mayan.apps.documents.tasks.document_tasks.task_document_upload',
    label=_('Upload new document')
)

queue_documents_file.add_task_type(
    dotted_path='mayan.apps.documents.tasks.document_file_tasks.task_document_file_checksum_update',
    label=_('Calculate and update document file checksum')
)
queue_documents_file.add_task_type(
    dotted_path='mayan.apps.documents.tasks.document_file_tasks.task_document_file_mimetype_update',
    label=_('Calculate and update document file MIME type')
)
queue_documents_file.add_task_type(
    dotted_path='mayan.apps.documents.tasks.document_file_tasks.task_document_file_page_count_update',
    label=_('Update document file page count')
)
queue_documents_file.add_task_type(
    dotted_path='mayan.apps.documents.tasks.document_file_tasks.task_document_file_size_update',
    label=_('Update document file size')
)
queue_documents_file.add_task_type(
    dotted_path='mayan.apps.documents.tasks.document_file_tasks.task_document_file_version_create',
    label=_('Create a new version after the file is processed')
)

queue_documents_file_slow.add_task_type(
    dotted_path='mayan.apps.documents.tasks.document_file_tasks.task_document_file_delete',
    label=_('Delete a document file')
)

queue_documents_periodic.add_task_type(
    dotted_path='mayan.apps.documents.tasks.document_type_tasks.task_document_type_document_trash_periods_check',
    label=_('Check document type trash periods'),
    name='task_document_type_document_trash_periods_check',
    schedule=timedelta(seconds=CHECK_TRASH_PERIOD_INTERVAL),
)
queue_documents_periodic.add_task_type(
    dotted_path='mayan.apps.documents.tasks.document_type_tasks.task_document_type_document_stubs_delete',
    label=_('Delete document stubs'),
    name='task_document_type_document_stubs_delete',
    schedule=timedelta(seconds=INTERVAL_TASK_STUBS_DELETION),
)
queue_documents_periodic.add_task_type(
    dotted_path='mayan.apps.documents.tasks.document_type_tasks.task_document_type_trashed_document_delete_periods_check',
    label=_('Check document type delete periods'),
    name='task_document_type_trashed_document_delete_periods_check',
    schedule=timedelta(
        seconds=CHECK_DELETE_PERIOD_INTERVAL
    )
)

queue_documents_trash.add_task_type(
    dotted_path='mayan.apps.documents.tasks.trashed_document_tasks.task_trash_can_empty',
    label=_('Empty the trash can')
)
queue_documents_trash.add_task_type(
    dotted_path='mayan.apps.documents.tasks.trashed_document_tasks.task_trashed_document_delete',
    label=_('Delete a document')
)

queue_documents_version.add_task_type(
    dotted_path='mayan.apps.documents.tasks.document_version_tasks.task_document_version_page_list_append',
    label=_('Append all document file pages to a document version')
)
queue_documents_version.add_task_type(
    dotted_path='mayan.apps.documents.tasks.document_version_tasks.task_document_version_page_list_reset',
    label=_('Reset the page list of a document version')
)
queue_documents_version.add_task_type(
    dotted_path='mayan.apps.documents.tasks.document_version_tasks.task_document_version_export',
    label=_('Export a document version')
)
queue_documents_version.add_task_type(
    dotted_path='mayan.apps.documents.tasks.document_version_tasks.task_document_version_delete',
    label=_('Delete a document version')
)
