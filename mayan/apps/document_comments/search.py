from django.utils.translation import ugettext_lazy as _

from mayan.apps.documents.search import search_model_document

# Document

search_model_document.add_model_field(
    field='comments__text', label=_('Comments')
)
