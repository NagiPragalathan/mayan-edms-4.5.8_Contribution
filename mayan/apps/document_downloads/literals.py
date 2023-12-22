from django.utils.translation import ugettext_lazy as _

DEFAULT_DOCUMENT_FILE_DOWNLOAD_MESSAGE_BODY = _(
    'The document files have been compressed '
    'and are available for download using the '
    'link: {{ download_url }} or from '
    'the downloads area ({{ download_list_url }}).'
)
DEFAULT_DOCUMENT_FILE_DOWNLOAD_MESSAGE_SUBJECT = _(
    'Document files ready for download.'
)
