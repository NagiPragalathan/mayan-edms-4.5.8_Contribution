import logging

from django.conf import settings
from django.contrib import messages
from django.core.files import File
from django.utils.translation import ugettext_lazy as _

from mayan.apps.sources.literals import STORAGE_NAME_SOURCE_CACHE_FOLDER
from mayan.apps.storage.classes import DefinedStorage

from ..classes import SourceStoredFile
from ..forms import StoredFileUploadForm
from ..source_backend_actions.stored_file_actions import (
    SourceBackendActionFileStoredDeleteInteractive,
    SourceBackendActionFileStoredDeleteInteractiveNot,
    SourceBackendActionFileStoredDocumentFileUpload,
    SourceBackendActionFileStoredDocumentUpload,
    SourceBackendActionFileStoredImage, SourceBackendActionFileStoredList
)
from ..views import SourceBackendStoredFileSourceFileListView

logger = logging.getLogger(name=__name__)


class SourceBackendMixinStoredFileUploadBase:
    upload_form_class = StoredFileUploadForm

    @classmethod
    def get_form_fields(cls):
        fields = super().get_form_fields()

        fields.update(
            {
                'delete_after_upload': {
                    'class': 'django.forms.BooleanField',
                    'help_text': _(
                        'Delete the file after is has been successfully '
                        'uploaded.'
                    ),
                    'label': _('Delete after upload'),
                    'required': False
                }
            }
        )

        return fields

    @classmethod
    def get_form_fieldsets(cls):
        fieldsets = super().get_form_fieldsets()

        fieldsets += (
            (
                _('File content'), {
                    'fields': (
                        'delete_after_upload',
                    ),
                },
            ),
        )

        return fieldsets

    def get_view_context(self, context, request):
        try:
            source_stored_file_list = list(
                self.get_stored_file_list()
            )
        except Exception as exception:
            messages.error(
                message=_(
                    'Unable get list of files; %s'
                ) % exception, request=request
            )
            source_stored_file_list = ()
            if settings.DEBUG or settings.TESTING:
                raise

        # Instantiate a fake list view to populate the pagination data for
        # the staging source file list.
        view = SourceBackendStoredFileSourceFileListView()
        view.kwargs = self.kwargs
        view.object_list = source_stored_file_list
        view.request = request

        template_source_stored_file_list_context = {
            'hide_link': True,
            'no_results_icon': self.icon,
            'no_results_text': _(
                'This could mean that the source file list is empty. It '
                'could also mean that the operating system user account '
                'being used for Mayan EDMS doesn\'t have the necessary '
                'file system permissions to access the source files.'
            ),
            'no_results_title': _('No source files available')
        }

        template_source_stored_file_list_context.update(
            view.get_context_data()
        )

        subtemplates_list = [
            {
                'context': {
                    'forms': context['forms']
                },
                'name': 'appearance/generic_multiform_subtemplate.html'
            },
            {
                'context': template_source_stored_file_list_context,
                'name': 'appearance/generic_list_subtemplate.html'
            }
        ]

        return {
            'subtemplates_list': subtemplates_list
        }


class SourceBackendMixinStoredFileDocumentFileUpload(
    SourceBackendMixinStoredFileUploadBase
):
    def get_action_class_list(self):
        action_class_list = super().get_action_class_list()

        action_class_list += (
            SourceBackendActionFileStoredDocumentFileUpload,
        )

        return action_class_list


class SourceBackendMixinStoredFileDocumentUpload(
    SourceBackendMixinStoredFileUploadBase
):
    def get_action_class_list(self):
        action_class_list = super().get_action_class_list()

        action_class_list += (SourceBackendActionFileStoredDocumentUpload,)

        return action_class_list


class SourceBackendMixinStoredFileDeleteInteractive:
    def action_file_delete(self, encoded_filename):
        source_stored_file = self.get_stored_file(
            encoded_filename=encoded_filename
        )

        source_stored_file.delete()

    def get_action_class_list(self):
        action_class_list = super().get_action_class_list()

        action_class_list += (
            SourceBackendActionFileStoredDeleteInteractive,
        )

        return action_class_list


class SourceBackendMixinStoredFileDeleteInteractiveNot:
    def action_file_delete(self, encoded_filename):
        source_stored_file = self.get_stored_file(
            encoded_filename=encoded_filename
        )

        source_stored_file.delete()

    def get_action_class_list(self):
        action_class_list = super().get_action_class_list()

        action_class_list += (
            SourceBackendActionFileStoredDeleteInteractiveNot,
        )

        return action_class_list


class SourceBackendMixinStoredFileImage:
    @classmethod
    def get_form_fields(cls):
        fields = super().get_form_fields()

        fields.update(
            {
                'preview_width': {
                    'class': 'django.forms.IntegerField',
                    'help_text': _(
                        'Width value to be passed to the converter backend.'
                    ),
                    'kwargs': {
                        'min_value': 0
                    },
                    'label': _('Preview width'),
                    'required': True
                },
                'preview_height': {
                    'class': 'django.forms.IntegerField',
                    'help_text': _(
                        'Height value to be passed to the converter backend.'
                    ),
                    'kwargs': {
                        'min_value': 0
                    },
                    'label': _('Preview height'),
                    'required': False
                },
                'preview_max_size': {
                    'class': 'django.forms.IntegerField',
                    'default': SourceStoredFile.DEFAULT_PREVIEW_MAX_SIZE,
                    'help_text': _(
                        'Maximum size in bytes for which previews will be '
                        'generated. Example: 20000 = 20KB.'
                    ),
                    'label': _('Max size preview'),
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
                _('File images'), {
                    'fields': (
                        'preview_width', 'preview_height',
                        'preview_max_size'
                    ),
                },
            ),
        )

        return fieldsets

    def action_file_image(
        self, encoded_filename, maximum_layer_order=None,
        transformation_instance_list=None, user=None
    ):
        if maximum_layer_order:
            maximum_layer_order = int(maximum_layer_order)

        source_stored_file = self.get_stored_file(
            encoded_filename=encoded_filename
        )

        combined_transformation_list = source_stored_file.get_combined_transformation_list(
            maximum_layer_order=maximum_layer_order,
            transformation_instance_list=transformation_instance_list,
            user=user
        )

        cache_filename = source_stored_file.generate_image(
            transformation_instance_list=combined_transformation_list
        )

        storage_source_stored_file_image_cache = DefinedStorage.get(
            name=STORAGE_NAME_SOURCE_CACHE_FOLDER
        ).get_storage_instance()

        def file_generator():
            with storage_source_stored_file_image_cache.open(name=cache_filename) as file_object:
                while True:
                    chunk = file_object.read(File.DEFAULT_CHUNK_SIZE)
                    if not chunk:
                        break
                    else:
                        yield chunk

        return file_generator

    def get_action_class_list(self):
        action_class_list = super().get_action_class_list()

        action_class_list += (SourceBackendActionFileStoredImage,)

        return action_class_list


class SourceBackendMixinStoredFileList:
    def action_file_list(self):
        for source_stored_file in self.get_stored_file_list():
            yield {
                'encoded_filename': source_stored_file.encoded_filename,
                'filename': source_stored_file.filename,
                'size': source_stored_file.get_size()
            }

    def get_action_class_list(self):
        action_class_list = super().get_action_class_list()

        action_class_list += (SourceBackendActionFileStoredList,)

        return action_class_list
