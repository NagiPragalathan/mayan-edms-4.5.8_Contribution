from django.conf.urls import url

from .api_views import APIDocumentVersionExportView
from .views import DocumentVersionExportView

urlpatterns = [
    url(
        regex=r'^documents/versions/(?P<document_version_id>\d+)/export/$',
        name='document_version_export',
        view=DocumentVersionExportView.as_view()
    )
]

api_urls = [
    url(
        regex=r'^documents/(?P<document_id>[0-9]+)/versions/(?P<document_version_id>[0-9]+)/export/$',
        view=APIDocumentVersionExportView.as_view(),
        name='documentversion-export'
    )
]
