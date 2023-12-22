from django.utils.translation import ugettext_lazy as _

from mayan.apps.acls.models import AccessControlList
from mayan.apps.documents.models.document_models import Document
from mayan.apps.documents.permissions import permission_document_view


class CabinetBusinessLogicMixin:
    def _get_documents(self):
        return Document.valid.filter(
            pk__in=self.documents.values('pk')
        )

    def document_add(self, document, user):
        return self._document_add(document=document, user=user)

    def document_remove(self, document, user):
        return self._document_remove(document=document, user=user)

    def get_document_count(self, user):
        """
        Return numeric count of the total documents in a cabinet. The count
        is filtered by access.
        """
        return self.get_documents(
            permission=permission_document_view, user=user
        ).count()

    def get_documents(self, permission, user):
        """
        Provide a queryset of the documents in a cabinet. The queryset is
        filtered by access.
        """
        return AccessControlList.objects.restrict_queryset(
            permission=permission, queryset=self._get_documents(),
            user=user
        )

    def get_full_path(self):
        """
        Returns a string that represents the path to the cabinet. The
        path string starts from the root cabinet.
        """
        result = []
        for node in self.get_ancestors(include_self=True):
            result.append(node.label)

        return ' / '.join(result)
    get_full_path.help_text = _(
        'The path to the cabinet including all ancestors.'
    )
    get_full_path.short_description = _('Full path')
