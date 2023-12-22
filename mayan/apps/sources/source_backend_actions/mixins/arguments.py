from django.utils.translation import ugettext_lazy as _

from mayan.apps.documents.literals import DEFAULT_DOCUMENT_FILE_ACTION_NAME
from mayan.apps.documents.models.document_file_models import DocumentFile
from mayan.apps.documents.models.document_models import Document

from ..interface_arguments import SourceBackendActionInterfaceArgument

from .literals import DEFAULT_IMMEDIATE_MODE


argument_document_help_text = _(
    'Document to which a new file will be uploaded to.'
)
argument_document_type = SourceBackendActionInterfaceArgument(
    help_text=Document.description.field.help_text
)
argument_immediate_mode_help_text = _(
    'When enabled, a document stub is created immediately and '
    'returned. The document file is processed asynchronously. When '
    'disabled, the entire process happens asynchronously with no '
    'returned data. Enabling immediate mode, disables compressed file '
    'processing.'
)

argument_document = SourceBackendActionInterfaceArgument(
    help_text=argument_document_help_text
)
argument_document_description = SourceBackendActionInterfaceArgument(
    default=None, help_text=Document.description.field.help_text,
    required=False
)
argument_document_label = SourceBackendActionInterfaceArgument(
    default=None, help_text=Document.label.field.help_text, required=False
)
argument_document_language = SourceBackendActionInterfaceArgument(
    default=None, help_text=Document.language.field.help_text, required=False
)
argument_document_id = SourceBackendActionInterfaceArgument(
    help_text=_(
        'ID of the document to which a new file will be uploaded to.'
    )
)
argument_document_id_optional = SourceBackendActionInterfaceArgument(
    default=None, help_text=argument_document_help_text, required=False
)

argument_document_file_action_name = SourceBackendActionInterfaceArgument(
    default=DEFAULT_DOCUMENT_FILE_ACTION_NAME,
    help_text=DocumentFile.versions_new.help_text, required=False
)
argument_document_file_comment = SourceBackendActionInterfaceArgument(
    default=None, help_text=DocumentFile.comment.field.help_text,
    required=False
)
argument_document_file_filename = SourceBackendActionInterfaceArgument(
    default=None, help_text=DocumentFile.filename.field.help_text,
    required=False
)

argument_document_type_id = SourceBackendActionInterfaceArgument(
    help_text=_('ID of the document type.')
)

argument_immediate_mode_optional = SourceBackendActionInterfaceArgument(
    default=DEFAULT_IMMEDIATE_MODE,
    help_text=argument_immediate_mode_help_text, required=False
)
argument_immediate_mode_required = SourceBackendActionInterfaceArgument(
    help_text=argument_immediate_mode_help_text
)

argument_user = SourceBackendActionInterfaceArgument(
    default=None, help_text=_(
        'User that will feature as the actor in the events.'
    ), required=False
)
argument_user_id = SourceBackendActionInterfaceArgument(
    default=None, help_text=_(
        'ID of the user that will feature as the actor in '
        'the events.'
    ), required=False
)
