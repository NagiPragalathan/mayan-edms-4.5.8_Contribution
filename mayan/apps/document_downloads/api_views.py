from mayan.apps.rest_api import generics
from mayan.apps.documents.api_views.api_view_mixins import (
    ParentObjectDocumentAPIViewMixin
)
from mayan.apps.views.generics import DownloadViewMixin

from .permissions import permission_document_file_download


class APIDocumentFileDownloadView(
    DownloadViewMixin, ParentObjectDocumentAPIViewMixin,
    generics.RetrieveAPIView
):
    """
    get: Download a document file.
    """
    lookup_url_kwarg = 'document_file_id'
    mayan_object_permissions = {
        'GET': (permission_document_file_download,),
    }

    def get_download_file_object(self):
        instance = self.get_object()
        instance._event_actor = self.request.user
        return instance.get_download_file_object()

    def get_download_filename(self):
        return self.get_object().filename

    def get_serializer(self, *args, **kwargs):
        return None

    def get_serializer_class(self):
        return None

    def get_source_queryset(self):
        return self.get_document().files.all()

    def retrieve(self, request, *args, **kwargs):
        return self.render_to_response()
