import json
import logging

from django.apps import apps
from django.utils.translation import ugettext_lazy as _

from mayan.apps.source_compressed.source_backends.literals import SOURCE_UNCOMPRESS_NON_INTERACTIVE_CHOICES
from mayan.apps.source_compressed.source_backends.mixins import SourceBackendMixinCompressed
from mayan.apps.sources.literals import SOURCE_ACTION_EXECUTE_TASK_PATH

from .literals import DEFAULT_PERIOD_INTERVAL, SOURCE_PERIODIC_ACTION_NAME

logger = logging.getLogger(name=__name__)


class SourceBackendMixinPeriodic:
    @classmethod
    def get_form_fields(cls):
        DocumentType = apps.get_model(
            app_label='documents', model_name='DocumentType'
        )

        fields = super().get_form_fields()
        fields.update(
            {
                'document_type_id': {
                    'class': 'django.forms.ChoiceField',
                    'default': '',
                    'help_text': _(
                        'Assign a document type to documents uploaded from this '
                        'source.'
                    ),
                    'kwargs': {
                        'choices': [
                            (document_type.id, document_type) for document_type in DocumentType.objects.all()
                        ],
                    },
                    'label': _('Document type'),
                    'required': True
                },
                'interval': {
                    'class': 'django.forms.IntegerField',
                    'default': DEFAULT_PERIOD_INTERVAL,
                    'help_text': _(
                        'Interval in seconds between checks for new '
                        'documents.'
                    ),
                    'kwargs': {
                        'min_value': 0
                    },
                    'label': _('Interval'),
                    'required': True
                }
            }
        )

        return fields

    @classmethod
    def get_form_fieldsets(cls):
        fieldsets = super().get_form_fieldsets()

        fieldsets += (
            (
                _('Unattended'), {
                    'fields': ('document_type_id', 'interval')
                },
            ),
        )

        return fieldsets

    @classmethod
    def get_form_widgets(cls):
        widgets = super().get_form_widgets()

        widgets.update(
            {
                'document_type_id': {
                    'class': 'django.forms.widgets.Select', 'kwargs': {
                        'attrs': {'class': 'select2'}
                    }
                }
            }
        )

        return widgets

    def create(self):
        super().create()

        IntervalSchedule = apps.get_model(
            app_label='django_celery_beat', model_name='IntervalSchedule'
        )
        PeriodicTask = apps.get_model(
            app_label='django_celery_beat', model_name='PeriodicTask'
        )

        # Create a new interval or use an existing one.
        interval_instance, created = IntervalSchedule.objects.get_or_create(
            every=self.kwargs['interval'], period='seconds'
        )

        PeriodicTask.objects.create(
            interval=interval_instance, kwargs=json.dumps(
                obj={
                    'action_name': SOURCE_PERIODIC_ACTION_NAME,
                    'source_id': self.model_instance_id
                }
            ), name=self.get_periodic_task_name(),
            task=SOURCE_ACTION_EXECUTE_TASK_PATH
        )

    def delete(self):
        super().delete()

        self.delete_periodic_task(pk=self.model_instance_id)

    def delete_periodic_task(self, pk=None):
        PeriodicTask = apps.get_model(
            app_label='django_celery_beat', model_name='PeriodicTask'
        )
        try:
            periodic_task = PeriodicTask.objects.get(
                name=self.get_periodic_task_name(pk=pk)
            )

            interval_instance = periodic_task.interval

            if tuple(interval_instance.periodictask_set.values_list('id', flat=True)) == (periodic_task.pk,):
                # Only delete the interval if nobody else is using it.
                interval_instance.delete()
            else:
                periodic_task.delete()
        except PeriodicTask.DoesNotExist:
            logger.warning(
                'Tried to delete non existent periodic task "%s"',
                self.get_periodic_task_name(pk=pk)
            )

    def get_allow_action_execute(self, action, action_execute_kwargs=None):
        return self.get_model_instance().enabled or action_execute_kwargs.get('dry_run', False)

    def get_document_type(self):
        DocumentType = apps.get_model(
            app_label='documents', model_name='DocumentType'
        )

        return DocumentType.objects.get(
            pk=self.kwargs['document_type_id']
        )

    def get_periodic_task_name(self, pk=None):
        return 'check_interval_source-{}'.format(
            pk or self.model_instance_id
        )

    def update(self):
        super().update()
        self.delete_periodic_task()
        self.create()


class SourceBackendMixinPeriodicCompressed(
    SourceBackendMixinCompressed, SourceBackendMixinPeriodic
):
    uncompress_choices = SOURCE_UNCOMPRESS_NON_INTERACTIVE_CHOICES
