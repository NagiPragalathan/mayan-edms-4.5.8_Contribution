import logging

from celery.backends.base import DisabledBackend

from django.apps import apps
from django.conf import settings
from django.utils.translation import ugettext_lazy as _

from mayan.apps.common.apps import MayanAppConfig
from mayan.apps.common.menus import menu_list_facet, menu_tools, menu_return
from mayan.apps.common.signals import signal_perform_upgrade
from mayan.apps.navigation.classes import SourceColumn
from mayan.apps.views.column_widgets import TwoStateWidget
from mayan.celery import app as celery_app

from .classes import CeleryQueue, TaskType, Task, Worker
from .handlers import handler_perform_upgrade
from .links import (
    link_queue_task_type_list, link_worker_list, link_worker_queue_list
)
from .literals import TEST_CELERY_RESULT_KEY, TEST_CELERY_RESULT_VALUE
from .methods import factory_method_periodic_task_save

logger = logging.getLogger(name=__name__)


class TaskManagerApp(MayanAppConfig):
    app_namespace = 'task_manager'
    app_url = 'task_manager'
    has_tests = True
    name = 'mayan.apps.task_manager'
    verbose_name = _('Task manager')

    def check_broker_connectivity(self):
        connection = celery_app.connection()

        logger.debug('Starting Celery broker connectivity test')
        try:
            connection.ensure_connection(
                interval_step=0, interval_max=0, interval_start=0,
                timeout=0.1
            )
        except Exception as exception:
            print(
                'Failed to connect to the Celery broker at {}; {}'.format(
                    connection.as_uri(), exception
                )
            )
            raise
        else:
            connection.release()

    def check_results_backend_connectivity(self):
        backend = celery_app.backend

        if not isinstance(backend, DisabledBackend):
            retry_policy = backend.retry_policy

            backend.retry_policy = {
                'max_retries': 0, 'interval_start': 0, 'interval_step': 1,
                'interval_max': 1
            }

            logger.debug('Starting Celery result backend connectivity test')
            try:
                backend.set(
                    key=TEST_CELERY_RESULT_KEY,
                    value=TEST_CELERY_RESULT_VALUE
                )
            except Exception as exception:
                print(
                    'Failed to connect to the Celery result backend at {}; {}'.format(
                        backend.as_uri(), exception
                    )
                )
                raise
            else:
                backend.delete(key=TEST_CELERY_RESULT_KEY)
                backend.retry_policy = retry_policy

    def ready(self):
        super().ready()

        PeriodicTask = apps.get_model(
            app_label='django_celery_beat', model_name='PeriodicTask'
        )

        try:
            self.check_broker_connectivity()
        except Exception as exception:
            print(
                'Error checking Celery broker connectivity: {}'.format(exception)
            )
            exit(1)

        try:
            self.check_results_backend_connectivity()
        except Exception as exception:
            print(
                'Error checking Celery result backend connectivity: {}'.format(exception)
            )
            exit(1)

        CeleryQueue.load_modules()

        if settings.DEBUG or settings.TESTING:
            PeriodicTask.add_to_class(
                name='save', value=factory_method_periodic_task_save(
                    super_save=PeriodicTask.save
                )
            )

        SourceColumn(
            attribute='label', is_identifier=True, label=_('Label'),
            source=CeleryQueue
        )
        SourceColumn(
            attribute='name', include_label=True, label=_('Name'),
            source=CeleryQueue
        )
        SourceColumn(
            attribute='default_queue', include_label=True,
            label=_('Default queue?'), source=CeleryQueue,
            widget=TwoStateWidget
        )
        SourceColumn(
            attribute='transient', help_text=_(
                'Transient queues are not persistent. Tasks in a transient '
                'queue are lost if the broker is restarted. Transient '
                'queues use less resources and managed non critical tasks.'
            ), include_label=True, label=_('Is transient?'),
            source=CeleryQueue, widget=TwoStateWidget
        )
        SourceColumn(
            attribute='get_task_type_count', source=CeleryQueue
        )

        SourceColumn(
            attribute='label', label=_('Label'), source=TaskType
        )
        SourceColumn(
            attribute='name', label=_('Name'), source=TaskType
        )
        SourceColumn(
            attribute='dotted_path', label=_('Dotted path'), source=TaskType
        )
        SourceColumn(
            attribute='schedule', label=_('Schedule'), source=TaskType
        )

        SourceColumn(
            attribute='task_type', include_label=True, label=_('Type'),
            source=Task
        )
        SourceColumn(
            attribute='get_time_started', include_label=True,
            label=_('Start time'), source=Task
        )
        SourceColumn(
            func=lambda context: context['object'].kwargs['hostname'],
            include_label=True, label=_('Host'), source=Task
        )
        SourceColumn(
            func=lambda context: context['object'].kwargs['args'],
            include_label=True, label=_('Arguments'), source=Task
        )
        SourceColumn(
            func=lambda context: context['object'].kwargs['kwargs'],
            include_label=True, label=_('Keyword arguments'), source=Task
        )
        SourceColumn(
            func=lambda context: context['object'].kwargs['worker_pid'],
            include_label=True, label=_('Worker process ID'), source=Task
        )

        SourceColumn(
            attribute='label', is_identifier=True, label=_('Label'),
            source=Worker
        )
        SourceColumn(
            attribute='name', label=_('Name'), source=Worker
        )
        SourceColumn(
            attribute='maximum_memory_per_child', help_text=_(
                'Maximum amount of resident memory a worker can execute '
                'before it\'s replaced by a new process.'
            ), label=_('Maximum memory per child'), source=Worker
        )
        SourceColumn(
            attribute='maximum_tasks_per_child', help_text=_(
                'Maximum number of tasks a worker can execute before it\'s '
                'replaced by a new process.'
            ), label=_('Maximum tasks per child'), source=Worker
        )
        SourceColumn(
            attribute='concurrency', help_text=_(
                'The number of worker processes/threads to launch. '
                'Defaults to the number of CPUs available on the machine.'
            ), label=_('Concurrency'), source=Worker
        )
        SourceColumn(
            attribute='nice_level', help_text=_(
                'The nice value determines the priority of the process. '
                'A higher value lowers the priority. The default '
                'value is 0.'
            ), label=_('Nice level'), source=Worker
        )
        SourceColumn(attribute='get_queue_count', source=Worker)

        menu_list_facet.bind_links(
            links=(link_queue_task_type_list,), sources=(CeleryQueue,)
        )
        menu_list_facet.bind_links(
            links=(link_worker_queue_list,), sources=(Worker,)
        )
        menu_return.bind_links(
            links=(link_worker_list,),
            sources=(Worker, 'task_manager:worker_list')
        )
        menu_tools.bind_links(
            links=(link_worker_list,)
        )

        signal_perform_upgrade.connect(
            dispatch_uid='task_manager_handler_perform_upgrade',
            receiver=handler_perform_upgrade
        )
