import logging

from django.conf import settings
from django.contrib import messages
from django.template import RequestContext
from django.urls import reverse
from django.utils.translation import ugettext_lazy as _
from django.views.generic.base import RedirectView

from mayan.apps.views.generics import (
    ConfirmView, FormView, SingleObjectListView
)
from mayan.apps.views.literals import LIST_MODE_CHOICE_ITEM

from .exceptions import DynamicSearchException
from .forms import SearchForm, AdvancedSearchForm
from .icons import (
    icon_result_list, icon_search, icon_search_advanced,
    icon_search_backend_reindex, icon_search_submit
)
from .links import link_search_again
from .literals import QUERY_PARAMETER_ANY_FIELD, SEARCH_MODEL_NAME_KWARG
from .permissions import permission_search_tools
from .search_backends import SearchBackend
from .settings import setting_match_all_default_value
from .tasks import task_reindex_backend
from .view_mixins import (
    SearchModelViewMixin, SearchQueryViewMixin, SearchResultViewMixin
)

logger = logging.getLogger(name=__name__)


class SearchAgainView(SearchQueryViewMixin, RedirectView):
    query_string = True

    def get_redirect_url(self, *args, **kwargs):
        query_dict = self.get_search_query()

        search_term_any_field = query_dict.get(
            QUERY_PARAMETER_ANY_FIELD, ''
        ).strip()

        if search_term_any_field:
            self.pattern_name = 'search:search_simple'
        else:
            self.pattern_name = 'search:search_advanced'

        return super().get_redirect_url(*args, **kwargs)


class SearchBackendReindexView(ConfirmView):
    view_icon = icon_search_backend_reindex
    view_permission = permission_search_tools

    def get_extra_context(self):
        context = {
            'subtitle': _(
                'This tool erases and populates the search backend\'s '
                'internal index.'
            ),
            'title': _('Reindex search backend')
        }

        search_backend_class = SearchBackend.get_class()

        if search_backend_class.feature_reindex:
            context['message'] = _(
                'This tool is required only for some search backends. '
                'Search results will be affected while the backend is '
                'being reindexed.'
            )
        else:
            context['message'] = _(
                'The currently selected search backend does not support or '
                'requires reindexing.'
            )

        return context

    def get_post_action_redirect(self):
        return reverse(viewname='common:tools_list')

    def view_action(self):
        task_reindex_backend.apply_async()

        messages.success(
            message=_('Search backend reindexing queued.'),
            request=self.request
        )


class SearchSimpleView(SearchModelViewMixin, SearchQueryViewMixin, FormView):
    template_name = 'appearance/generic_form.html'
    view_icon = icon_search

    def get_extra_context(self):
        self.search_model = self.get_search_model()
        return {
            'form': self.get_form(),
            'form_action': reverse(
                viewname='search:search_results', kwargs={
                    SEARCH_MODEL_NAME_KWARG: self.search_model.full_name
                }
            ),
            'search_model': self.search_model,
            'submit_icon': icon_search_submit,
            'submit_label': _('Search'),
            'submit_method': 'GET',
            'title': _('Search for: %s') % self.search_model.label
        }

    def get_form(self):
        query_dict = self.get_search_query()

        search_term_any_field = query_dict.get(
            QUERY_PARAMETER_ANY_FIELD, ''
        ).strip()

        if search_term_any_field:
            return SearchForm(
                initial={
                    QUERY_PARAMETER_ANY_FIELD: search_term_any_field
                }
            )
        else:
            return SearchForm()


class SearchAdvancedView(SearchSimpleView):
    view_icon = icon_search_advanced

    def get_extra_context(self):
        context = super().get_extra_context()

        context.update(
            {
                'title': _(
                    'Advanced search for: %s'
                ) % self.search_model.label
            }
        )

        return context

    def get_form(self):
        data = self.request.GET.dict()
        data['_match_all'] = data.get(
            '_match_all', setting_match_all_default_value.value
        )

        return AdvancedSearchForm(
            data=data, search_model=self.get_search_model()
        )


class SearchResultsView(
    SearchModelViewMixin, SearchResultViewMixin, SingleObjectListView
):
    view_icon = icon_result_list

    def get_extra_context(self):
        context = {
            'hide_object': True,
            'no_results_icon': icon_search_submit,
            'no_results_main_link': link_search_again.resolve(
                context=RequestContext(
                    dict_={
                        'search_model': self.search_model
                    }, request=self.request
                )
            ),
            'no_results_text': _(
                'Try again using different terms. '
            ),
            'no_results_title': _('No search results'),
            'search_model': self.search_model,
            'subtitle': _(
                'Search query: %s'
            ) % self.search_interpreter.to_explain(),
            'title': _('Search results for: %s') % self.search_model.label
        }

        if self.search_model.list_mode == LIST_MODE_CHOICE_ITEM:
            context['list_as_items'] = True

        return context

    def get_source_queryset(self):
        try:
            return self.get_search_queryset()
        except DynamicSearchException as exception:
            if settings.DEBUG or settings.TESTING:
                raise

            messages.error(message=exception, request=self.request)
            return self.search_model.get_queryset().none()
