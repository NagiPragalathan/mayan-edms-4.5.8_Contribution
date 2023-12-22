from unittest import mock

from django_celery_beat.models import PeriodicTask

from mayan.apps.documents.events import (
    event_document_created, event_document_file_created,
    event_document_version_created
)
from mayan.apps.documents.models.document_models import Document
from mayan.apps.documents.tests.base import GenericDocumentTestCase
from mayan.apps.sources.events import (
    event_source_created, event_source_edited
)

from .mixins import PeriodicSourceBackendTestMixin


class PeriodicSourceBackendTestCase(
    PeriodicSourceBackendTestMixin, GenericDocumentTestCase
):
    _test_source_create_auto = False
    auto_upload_test_document = False

    def test_periodic_source_create(self):
        periodic_task_count = PeriodicTask.objects.count()

        self._clear_events()

        self._test_source_create()

        self.assertEqual(
            PeriodicTask.objects.count(), periodic_task_count + 1
        )

        events = self._get_test_events()
        self.assertEqual(events.count(), 1)

        self.assertEqual(events[0].action_object, None)
        self.assertEqual(events[0].actor, self._test_source)
        self.assertEqual(events[0].target, self._test_source)
        self.assertEqual(events[0].verb, event_source_created.id)

    def test_periodic_source_delete(self):
        self._test_source_create()

        periodic_task_count = PeriodicTask.objects.count()

        self._clear_events()

        self._test_source.delete()

        self.assertEqual(
            PeriodicTask.objects.count(), periodic_task_count - 1
        )

        events = self._get_test_events()
        self.assertEqual(events.count(), 0)

    def test_periodic_source_update(self):
        self._test_source_create()

        periodic_task_count = PeriodicTask.objects.count()

        self._clear_events()

        self._test_source.save()

        self.assertEqual(
            PeriodicTask.objects.count(), periodic_task_count
        )

        events = self._get_test_events()
        self.assertEqual(events.count(), 1)

        self.assertEqual(events[0].action_object, None)
        self.assertEqual(events[0].actor, self._test_source)
        self.assertEqual(events[0].target, self._test_source)
        self.assertEqual(events[0].verb, event_source_edited.id)


class PeriodicSourceBackendActionTestCase(
    PeriodicSourceBackendTestMixin, GenericDocumentTestCase
):
    auto_upload_test_document = False

    @mock.patch(target='mayan.apps.source_periodic.tests.source_backends.SourceBackendTestPeriodic.action_file_delete')
    def test_dry_run_false(self, mocked_action_file_delete):
        self._silence_logger(name='mayan.apps.converter.backends')

        document_count = Document.objects.count()

        self._clear_events()

        self._execute_test_source_action(
            action_name='document_upload', extra_data={'dry_run': False}
        )

        self.assertEqual(mocked_action_file_delete.call_count, 1)

        self.assertEqual(Document.objects.count(), document_count + 1)

        events = self._get_test_events()
        self.assertEqual(events.count(), 3)

        test_document = Document.objects.first()
        test_document_file = test_document.file_latest
        test_document_version = test_document.version_active

        self.assertEqual(events[0].action_object, self._test_document_type)
        self.assertEqual(events[0].actor, test_document)
        self.assertEqual(events[0].target, test_document)
        self.assertEqual(events[0].verb, event_document_created.id)

        self.assertEqual(events[1].action_object, test_document)
        self.assertEqual(events[1].actor, test_document_file)
        self.assertEqual(events[1].target, test_document_file)
        self.assertEqual(events[1].verb, event_document_file_created.id)

        self.assertEqual(events[2].action_object, test_document)
        self.assertEqual(events[2].actor, test_document_version)
        self.assertEqual(events[2].target, test_document_version)
        self.assertEqual(events[2].verb, event_document_version_created.id)

    @mock.patch(target='mayan.apps.source_periodic.tests.source_backends.SourceBackendTestPeriodic.action_file_delete')
    def test_dry_run_true(self, mocked_action_file_delete):
        self._silence_logger(name='mayan.apps.converter.backends')

        document_count = Document.objects.count()

        self._clear_events()

        self._execute_test_source_action(
            action_name='document_upload', extra_data={'dry_run': True}
        )

        self.assertEqual(mocked_action_file_delete.call_count, 0)

        self.assertEqual(Document.objects.count(), document_count + 1)

        events = self._get_test_events()
        self.assertEqual(events.count(), 3)

        test_document = Document.objects.first()
        test_document_file = test_document.file_latest
        test_document_version = test_document.version_active

        self.assertEqual(events[0].action_object, self._test_document_type)
        self.assertEqual(events[0].actor, test_document)
        self.assertEqual(events[0].target, test_document)
        self.assertEqual(events[0].verb, event_document_created.id)

        self.assertEqual(events[1].action_object, test_document)
        self.assertEqual(events[1].actor, test_document_file)
        self.assertEqual(events[1].target, test_document_file)
        self.assertEqual(events[1].verb, event_document_file_created.id)

        self.assertEqual(events[2].action_object, test_document)
        self.assertEqual(events[2].actor, test_document_version)
        self.assertEqual(events[2].target, test_document_version)
        self.assertEqual(events[2].verb, event_document_version_created.id)

    @mock.patch(target='mayan.apps.source_periodic.tests.source_backends.SourceBackendTestPeriodic.action_file_delete')
    def test_dry_run_missing(self, mocked_action_file_delete):
        self._silence_logger(name='mayan.apps.converter.backends')

        document_count = Document.objects.count()

        self._clear_events()

        self._execute_test_source_action(action_name='document_upload')

        self.assertEqual(mocked_action_file_delete.call_count, 1)

        self.assertEqual(Document.objects.count(), document_count + 1)

        events = self._get_test_events()
        self.assertEqual(events.count(), 3)

        test_document = Document.objects.first()
        test_document_file = test_document.file_latest
        test_document_version = test_document.version_active

        self.assertEqual(events[0].action_object, self._test_document_type)
        self.assertEqual(events[0].actor, test_document)
        self.assertEqual(events[0].target, test_document)
        self.assertEqual(events[0].verb, event_document_created.id)

        self.assertEqual(events[1].action_object, test_document)
        self.assertEqual(events[1].actor, test_document_file)
        self.assertEqual(events[1].target, test_document_file)
        self.assertEqual(events[1].verb, event_document_file_created.id)

        self.assertEqual(events[2].action_object, test_document)
        self.assertEqual(events[2].actor, test_document_version)
        self.assertEqual(events[2].target, test_document_version)
        self.assertEqual(events[2].verb, event_document_version_created.id)
