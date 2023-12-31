from django.utils.translation import ugettext_lazy as _

from ..icons import icon_document_recently_accessed_list
from ..models.recently_accessed_document_models import RecentlyAccessedDocument

from .document_views import DocumentListView


from django.http import HttpResponse

def simple_string_view1(request):
    """
    A simple Django view that returns a string.
    """
    return HttpResponse("Hello, this is a simple string response. from one")


class RecentlyAccessedDocumentListView(DocumentListView):
    view_icon = icon_document_recently_accessed_list

    def get_document_queryset(self):
        return RecentlyAccessedDocument.valid.get_for_user(
            user=self.request.user
        )

    def get_extra_context(self):
        context = super().get_extra_context()
        context.update(
            {
                'no_results_icon': icon_document_recently_accessed_list,
                'no_results_text': _(
                    'This view will list the latest documents viewed or '
                    'manipulated in any way by this user account.'
                ),
                'no_results_title': _(
                    'There are no recently accessed documents'
                ),
                'title': _('Recently accessed')
            }
        )
        return context
