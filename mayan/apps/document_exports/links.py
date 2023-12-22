from django.utils.translation import ugettext_lazy as _

from mayan.apps.navigation.classes import Link

from .icons import icon_document_version_export
from .permissions import permission_document_version_export

link_document_version_export = Link(
    args='resolved_object.pk', icon=icon_document_version_export,
    permissions=(permission_document_version_export,),
    text=_('Export'), view='document_exports:document_version_export'
)
