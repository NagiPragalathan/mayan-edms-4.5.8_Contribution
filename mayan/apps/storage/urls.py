from django.conf.urls import url

from .api_views import (
    APIDownloadFileDetailView, APIDownloadFileDownloadView,
    APIDownloadFileListView
)
from .views import (
    DownloadFileDeleteView, DownloadFileDownloadViewView,
    DownloadFileListView
)

urlpatterns = [
    url(
        regex=r'^downloads/(?P<download_file_id>\d+)/delete/$',
        name='download_file_delete',
        view=DownloadFileDeleteView.as_view()
    ),
    url(
        regex=r'^downloads/(?P<download_file_id>\d+)/download/$',
        name='download_file_download',
        view=DownloadFileDownloadViewView.as_view()
    ),
    url(
        regex=r'^downloads/$', name='download_file_list',
        view=DownloadFileListView.as_view()
    )
]

api_urls = [
    url(
        regex=r'^downloads/$', view=APIDownloadFileListView.as_view(),
        name='download_file-list'
    ),
    url(
        regex=r'^downloads/(?P<download_file_id>[0-9]+)/$',
        view=APIDownloadFileDetailView.as_view(),
        name='download_file-detail'
    ),
    url(
        regex=r'^downloads/(?P<download_file_id>[0-9]+)/download/$',
        view=APIDownloadFileDownloadView.as_view(),
        name='download_file-download'
    )
]
