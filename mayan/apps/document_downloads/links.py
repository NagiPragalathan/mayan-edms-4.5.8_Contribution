from django.utils.translation import ugettext_lazy as _

from mayan.apps.navigation.classes import Link

from .icons import (
    icon_document_download_multiple, icon_document_download_single,
    icon_document_file_download_quick
)
from .permissions import permission_document_file_download

link_document_download_multiple = Link(
    icon=icon_document_download_multiple, text=_('Download files'),
    view='document_downloads:document_download_multiple'
)
link_document_download_single = Link(
    args='resolved_object.pk', icon=icon_document_download_single,
    permissions=(permission_document_file_download,),
    text=_('Download files'),
    view='document_downloads:document_download_single'
)
link_document_file_download_quick = Link(
    args='resolved_object.id', icon=icon_document_file_download_quick,
    permissions=(permission_document_file_download,), tags='new_window',
    text=_('Quick download'),
    view='document_downloads:document_file_download'
)
