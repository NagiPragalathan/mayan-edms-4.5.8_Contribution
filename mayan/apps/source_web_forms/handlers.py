from django.apps import apps
from django.utils.translation import ugettext_lazy as _

from mayan.apps.source_compressed.source_backends.literals import SOURCE_UNCOMPRESS_CHOICE_ASK

from .source_backends import SourceBackendWebForm


def handler_create_default_document_source(sender, **kwargs):
    Source = apps.get_model(
        app_label='sources', model_name='Source'
    )

    if not Source.objects.filter(backend_path=SourceBackendWebForm.get_class_path()).count():
        Source.objects.create_backend(
            backend_path=SourceBackendWebForm.get_class_path(),
            backend_data={
                'uncompress': SOURCE_UNCOMPRESS_CHOICE_ASK
            }, label=_('Default')
        )
