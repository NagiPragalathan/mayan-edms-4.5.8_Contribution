from django.apps import apps


def handler_delete_interval_source_periodic_task(sender, instance, **kwargs):
    Source = apps.get_model(
        app_label='sources', model_name='Source'
    )

    for source in Source.objects.all():
        backend_instance = source.get_backend_instance()

        if backend_instance.kwargs.get('document_type') == instance:
            try:
                backend_instance.delete_periodic_task()
            except AttributeError:
                """
                The source has a document type but is not a periodic source,
                """


def handler_initialize_periodic_tasks(sender, **kwargs):
    Source = apps.get_model(
        app_label='sources', model_name='Source'
    )

    for source in Source.objects.filter(enabled=True):
        backend_instance = source.get_backend_instance()
        backend_instance.update()
