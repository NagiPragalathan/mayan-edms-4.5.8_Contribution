from django.utils.translation import ugettext_lazy as _

from mayan.apps.smart_settings.classes import SettingNamespace

from .classes import DocumentFileCompressor
from .literals import (
    DEFAULT_DOCUMENT_FILE_DOWNLOAD_MESSAGE_BODY,
    DEFAULT_DOCUMENT_FILE_DOWNLOAD_MESSAGE_SUBJECT,
)

namespace = SettingNamespace(
    label=_('Document downloads'), name='document_downloads'
)

setting_message_body_template = namespace.add_setting(
    default=DEFAULT_DOCUMENT_FILE_DOWNLOAD_MESSAGE_BODY,
    global_name='DOCUMENT_FILE_DOWNLOAD_MESSAGE_BODY', help_text=_(
        'Template for the document download message body text. Can '
        'include HTML. Available variables: {}'.format(
            ', '.join(DocumentFileCompressor.context_key_list)
        )
    )
)
setting_message_subject_template = namespace.add_setting(
    default=DEFAULT_DOCUMENT_FILE_DOWNLOAD_MESSAGE_SUBJECT,
    global_name='DOCUMENT_FILE_DOWNLOAD_MESSAGE_SUBJECT', help_text=_(
        'Template for the document download message subject line. '
        'Can\'t include HTML. Available variables: {}'.format(
            ', '.join(DocumentFileCompressor.context_key_list)
        )
    )
)
