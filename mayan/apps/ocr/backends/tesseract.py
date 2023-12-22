import logging
import os

import sh

from django.utils.translation import ugettext_lazy as _

from ..classes import OCRBackendBase
from ..exceptions import OCRError

from .literals import (
    DEFAULT_TESSERACT_BINARY_PATH, DEFAULT_TESSERACT_TIMEOUT
)

logger = logging.getLogger(name=__name__)


class Tesseract(OCRBackendBase):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.read_settings()

        if kwargs.get('auto_initialize', True):
            self.initialize()

    def _execute(self, image_file_object):
        """
        Execute the command line binary of tesseract.
        """
        if self.command_tesseract:
            arguments = ['-', '-']

            keyword_arguments = {
                '_in': image_file_object,
                '_timeout': self.command_timeout
            }

            if self.language:
                keyword_arguments['l'] = self.language

            environment = os.environ.copy()
            environment.update(self.environment)
            keyword_arguments['_env'] = environment

            try:
                output = self.command_tesseract(
                    *arguments, **keyword_arguments
                )
            except Exception as exception:
                error_message_list = []
                error_message_list.append(
                    'Exception calling Tesseract with language option: {}; {}'.format(
                        self.language, exception
                    )
                )

                if self.language not in self.languages:
                    error_message_list.append(
                        'The requested OCR language "{}" is not '
                        'available and needs to be installed.'.format(
                            self.language
                        )
                    )

                error_message = '/n'.join(error_message_list)

                logger.error(error_message, exc_info=True)
                raise OCRError(error_message)
            else:
                return output
        else:
            return ''

    def initialize(self):
        self.languages = ()

        try:
            self.command_tesseract = sh.Command(
                path=self.tesseract_binary_path
            )
        except sh.CommandNotFound:
            self.command_tesseract = None
            raise OCRError(
                _('Tesseract OCR not found.')
            )
        else:
            # Get version.
            output = self.command_tesseract(v=True)
            logger.debug('Tesseract version: %s', output)

            # Get languages.
            output = self.command_tesseract(list_langs=True)
            # Sample output format.
            # List of available languages (3):
            # deu
            # eng
            # osd
            # <- empty line

            # Extaction: strip last line, split by newline, discard the first
            # line.
            self.languages = output.strip().split('\n')[1:]

            logger.debug(
                'Available languages: %s', ', '.join(self.languages)
            )

    def read_settings(self):
        self.command_timeout = self.kwargs.get(
            'timeout', DEFAULT_TESSERACT_TIMEOUT
        )
        self.environment = self.kwargs.get(
            'environment', {}
        )
        self.tesseract_binary_path = self.kwargs.get(
            'tesseract_path', DEFAULT_TESSERACT_BINARY_PATH
        )
