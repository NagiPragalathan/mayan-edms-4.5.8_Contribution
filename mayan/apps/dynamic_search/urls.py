from django.conf.urls import url

from .api_views import APISearchModelList, APISearchView
from .views import (
    SearchAdvancedView, SearchAgainView, SearchBackendReindexView,
    SearchResultsView, SearchSimpleView
)

urlpatterns_search = [
    url(
        regex=r'^again/(?P<search_model_pk>[\.\w]+)/$', name='search_again',
        view=SearchAgainView.as_view()
    ),
    url(
        regex=r'^advanced/(?P<search_model_pk>[\.\w]+)/$',
        name='search_advanced', view=SearchAdvancedView.as_view()
    ),
    url(
        regex=r'^advanced/$', name='search_advanced',
        view=SearchAdvancedView.as_view()
    ),
    url(
        regex=r'^results/$', name='search_results',
        view=SearchResultsView.as_view()
    ),
    url(
        regex=r'^results/(?P<search_model_pk>[\.\w]+)/$',
        name='search_results', view=SearchResultsView.as_view()
    ),
    url(
        regex=r'^simple/(?P<search_model_pk>[\.\w]+)/$',
        name='search_simple', view=SearchSimpleView.as_view()
    )
]

urlpatterns_tools = [
    url(
        regex=r'^backend/reindex/$', name='search_backend_reindex',
        view=SearchBackendReindexView.as_view()
    )
]

urlpatterns = []
urlpatterns.extend(urlpatterns_search)
urlpatterns.extend(urlpatterns_tools)

api_urls = [
    url(
        regex=r'^search/(?P<search_model_pk>[\.\w]+)/$', name='search-view',
        view=APISearchView.as_view()
    ),
    url(
        regex=r'^search/advanced/(?P<search_model_pk>[\.\w]+)/$',
        name='advanced-search-view', view=APISearchView.as_view()
    ),
    url(
        regex=r'^search_models/$', name='searchmodel-list',
        view=APISearchModelList.as_view()
    )
]
