import logging
import random

from flanker import mime

from django.core.files.base import ContentFile
from django.utils.encoding import force_bytes
from django.utils.translation import ugettext_lazy as _

from mayan.apps.credentials.class_mixins import BackendMixinCredentials
from mayan.apps.source_periodic.source_backends.mixins import SourceBackendMixinPeriodicCompressed

from ..source_backend_actions import SourceBackendActionEmailDocumentUpload

logger = logging.getLogger(name=__name__)


class SourceBackendMixinEmail(
    BackendMixinCredentials, SourceBackendMixinPeriodicCompressed
):
    action_class_list = (SourceBackendActionEmailDocumentUpload,)

    @classmethod
    def get_form_fields(cls):
        fields = super().get_form_fields()

        fields.update(
            {
                'host': {
                    'class': 'django.forms.CharField',
                    'label': _('Host'),
                    'kwargs': {
                        'max_length': 128
                    },
                    'required': True
                },
                'ssl': {
                    'class': 'django.forms.BooleanField',
                    'default': True,
                    'label': _('SSL'),
                    'required': False
                },
                'port': {
                    'class': 'django.forms.IntegerField',
                    'help_text': _(
                        'Typical choices are 110 for POP3, 995 for POP3 '
                        'over SSL, 143 for IMAP, 993 for IMAP over SSL.'
                    ),
                    'kwargs': {
                        'min_value': 0
                    },
                    'label': _('Port'),
                },
                'store_body': {
                    'class': 'django.forms.BooleanField',
                    'default': True,
                    'help_text': _(
                        'Store the body of the email as a text document.'
                    ),
                    'label': _('Store email body'),
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
                _('Common email options'), {
                    'fields': (
                        'host', 'ssl', 'port', 'store_body'
                    )
                },
            ),
        )

        return fieldsets

    def process_message(self, message):
        bytes_message = force_bytes(s=message)

        message = mime.from_string(string=bytes_message)

        return self._process_message_content(message=message)

    def _process_message_content(self, message):
        counter = 1
        # Messages are tree based, do nested processing of message parts until
        # a message with no children is found, then work our way up.
        if message.parts:
            for part in message.parts:
                yield from self._process_message_content(
                    message=part
                )
        else:
            # Treat inlines as attachments, both are extracted and saved as
            # documents.

            source_metadata = {
                'email_date': message.headers.get('Date'),
                'email_delivered_to': message.headers.get('Delivered-To'),
                'email_from': message.headers.get('From'),
                'email_message_id': message.headers.get('Message-ID'),
                'email_received': message.headers.get('Received'),
                'email_subject': message.headers.get('Subject'),
                'email_to': message.headers.get('To')
            }

            if message.is_attachment() or message.is_inline():
                # Reject zero length attachments.
                if len(message.body) != 0:
                    label = message.detected_file_name or 'attachment-{}'.format(counter)
                    counter += 1

                    yield {
                        'file': ContentFile(
                            content=message.body, name=label,
                        ), 'source_metadata': source_metadata
                    }
            else:
                # If it is not an attachment then it should be a body message
                # part. Another option is to use message.is_body().
                if message.detected_content_type == 'text/html':
                    label = 'email_body.html'
                else:
                    label = 'email_body.txt'

                if self.kwargs['store_body']:
                    yield {
                        'file': ContentFile(
                            content=force_bytes(s=message.body), name=label
                        ), 'source_metadata': source_metadata
                    }

    def get_file_identifier(self):
        file_list_generator = self.get_stored_file_list()

        file_list_generator = list(file_list_generator)

        if file_list_generator:
            return random.choice(seq=file_list_generator)
