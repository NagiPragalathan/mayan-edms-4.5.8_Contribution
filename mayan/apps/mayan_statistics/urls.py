from django.conf.urls import url

from .views import (
    StatisticNamespaceDetailView, StatisticNamespaceListView,
    StatisticTypeDetailView, StatisticTypeQueueView
)

urlpatterns = [
    url(
        regex=r'^namespaces/$', view=StatisticNamespaceListView.as_view(),
        name='statistic_namespace_list'
    ),
    url(
        regex=r'^namespaces/(?P<slug>[\w-]+)/$',
        view=StatisticNamespaceDetailView.as_view(),
        name='statistic_namespace_detail'
    ),
    url(
        regex=r'^namespaces/statistics/(?P<slug>[\w-]+)/view/$',
        view=StatisticTypeDetailView.as_view(), name='statistic_detail'
    ),
    url(
        regex=r'^namespaces/statistics/(?P<slug>[\w-]+)/queue/$',
        view=StatisticTypeQueueView.as_view(), name='statistic_queue'
    )
]
