import base64
import logging
from urllib.parse import quote_plus, unquote_plus

from furl import furl

from django.core.files.base import ContentFile
from django.template.defaultfilters import filesizeformat
from django.utils.encoding import force_text
from django.utils.functional import cached_property
from django.utils.translation import ugettext_lazy as _

from rest_framework.reverse import reverse as rest_framework_reverse

from mayan.apps.common.menus import menu_object
from mayan.apps.converter.classes import AppImageErrorImage, ConverterBase
from mayan.apps.converter.exceptions import AppImageError, InvalidOfficeFormat
from mayan.apps.converter.transformations import TransformationResize
from mayan.apps.navigation.classes import SourceColumn
from mayan.apps.sources.literals import STORAGE_NAME_SOURCE_CACHE_FOLDER
from mayan.apps.storage.classes import DefinedStorage

from .column_widgets import StoredFileThumbnailWidget
from .links import link_storage_file_delete, link_source_file_select

logger = logging.getLogger(name=__name__)


class SourceStoredFile:
    _initialized = False
    DEFAULT_PREVIEW_MAX_SIZE = 100000000
    IMAGE_ERROR_STAGING_FILE_TOO_LARGE = 'staging_file_too_large'

    @classmethod
    def initialize(cls):
        if not cls._initialized:
            AppImageErrorImage(
                name=SourceStoredFile.IMAGE_ERROR_STAGING_FILE_TOO_LARGE,
                template_name='source_stored_files/errors/staging_file_too_large.html'
            )

            SourceColumn(
                attribute='get_size_display',
                label=_('Size'), source=SourceStoredFile,
            )

            SourceColumn(
                label=_('Thumbnail'), source=SourceStoredFile,
                widget=StoredFileThumbnailWidget,
                html_extra_classes='text-center'
            )

            menu_object.bind_links(
                links=(link_source_file_select, link_storage_file_delete,),
                sources=(SourceStoredFile,)
            )

            cls._initialized = True

    def __init__(self, source, encoded_filename=None, filename=None):
        self.source = source
        if encoded_filename:
            self.encoded_filename = str(encoded_filename)

            try:
                self.filename = base64.urlsafe_b64decode(
                    s=unquote_plus(string=self.encoded_filename)
                ).decode('utf8')
            except UnicodeDecodeError:
                raise ValueError(
                    'Incorrect `encoded_filename` value.'
                )
        else:
            if not filename:
                raise KeyError(
                    'Supply either `encoded_filename` or `filename` when '
                    'instantiating a staging source file.'
                )
            self.filename = filename
            self.encoded_filename = quote_plus(
                base64.urlsafe_b64encode(
                    s=filename.encode('utf8')
                )
            )

    def __str__(self):
        return force_text(s=self.filename)

    @property
    def cache_filename(self):
        return '{}-{}'.format(
            self.source.model_instance_id, self.encoded_filename
        )

    def delete(self):
        # Don't include kwargs in .delete() as some backends might not
        # support them.
        try:
            self.image_cache_storage.delete(self.cache_filename)
        except FileNotFoundError:
            """No preview was yet generated."""

        self.storage_backend_instance.delete(
            name=self.get_full_path()
        )

    def generate_image(self, transformation_instance_list=None):
        # Check is transformed image is available.
        logger.debug(
            'transformations cache filename: %s', self.cache_filename
        )

        if self.image_cache_storage.exists(self.cache_filename):
            logger.debug(
                'staging file cache file "%s" found', self.cache_filename
            )
        else:
            logger.debug(
                'staging file cache file "%s" not found', self.cache_filename
            )
            image = self.get_image(
                transformation_instance_list=transformation_instance_list
            )

            # Since open "wb+" doesn't create files, check if the file
            # exists, if not then create it.
            self.image_cache_storage.save(
                content=ContentFile(content=b''), name=self.cache_filename
            )

            with self.image_cache_storage.open(name=self.cache_filename, mode='wb+') as file_object:
                file_object.write(
                    image.getvalue()
                )

        return self.cache_filename

    def get_api_image_url(
        self, maximum_layer_order=None, transformation_instance_list=None,
        request=None, user=None
    ):
        if self.get_size() > self.get_source_preview_max_size():
            raise AppImageError(
                error_name=SourceStoredFile.IMAGE_ERROR_STAGING_FILE_TOO_LARGE
            )

        final_url = furl()
        final_url.args = {'encoded_filename': self.encoded_filename}
        final_url.path = rest_framework_reverse(
            'rest_api:source_action-execute', kwargs={
                'action_name': 'file_image',
                'source_id': self.source.model_instance_id
            }, request=request
        )

        return final_url.tostr()

    def get_combined_transformation_list(
        self, maximum_layer_order=None, transformation_instance_list=None,
        user=None
    ):
        """
        Return a list of transformation containing the server side
        transformations for this object as well as transformations
        created from the arguments as transient interactive transformation.
        """
        result = [
            TransformationResize(
                height=self.source.kwargs.get('preview_height'),
                width=self.source.kwargs['preview_width']
            )
        ]

        # Interactive transformations second.
        result.extend(
            transformation_instance_list or []
        )

        return result

    def get_full_path(self):
        return self.filename

    def get_image(self, transformation_instance_list=None):
        if self.get_size() > self.get_source_preview_max_size():
            raise AppImageError(
                error_name=SourceStoredFile.IMAGE_ERROR_STAGING_FILE_TOO_LARGE
            )

        try:
            with self.open(mode='rb') as file_object:
                converter = ConverterBase.get_converter_class()(
                    file_object=file_object
                )

                try:
                    with converter.to_pdf() as pdf_file_object:
                        image_converter = ConverterBase.get_converter_class()(
                            file_object=pdf_file_object
                        )
                        page_image = image_converter.get_page()
                except InvalidOfficeFormat:
                    page_image = converter.get_page()
        except Exception as exception:
            # Cleanup in case of error.
            logger.error(
                'Error getting staging file image for file "%s"; %s',
                self.get_full_path(), exception
            )
            raise
        else:
            return page_image

    def get_size(self):
        return self.storage_backend_instance.size(
            name=self.get_full_path()
        )

    def get_size_display(self):
        return filesizeformat(
            bytes_=self.get_size()
        )

    def get_source_preview_max_size(self):
        return self.source.kwargs.get(
            'preview_max_size', SourceStoredFile.DEFAULT_PREVIEW_MAX_SIZE
        )

    @cached_property
    def image_cache_storage(self):
        return DefinedStorage.get(
            name=STORAGE_NAME_SOURCE_CACHE_FOLDER
        ).get_storage_instance()

    def open(self, mode=None):
        return self.storage_backend_instance.open(
            name=self.get_full_path(), mode=mode
        )

    @cached_property
    def storage_backend_instance(self):
        return self.source.get_storage_backend_instance()
