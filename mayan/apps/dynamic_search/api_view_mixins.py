from .view_mixins import SearchModelViewMixin


class SearchModelAPIViewMixin(SearchModelViewMixin):
    """Subclass to allow any REST API code to be added."""
