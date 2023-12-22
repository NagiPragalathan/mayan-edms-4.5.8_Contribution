import logging

from django.urls import reverse_lazy
from django.utils.translation import ugettext_lazy as _

from mayan.apps.views.generics import SingleObjectEditView

from ..icons import icon_document_type_retention_policies
from ..models.document_type_models import DocumentType
from ..permissions import permission_document_type_edit

logger = logging.getLogger(name=__name__)


class DocumentTypeRetentionPoliciesEditView(SingleObjectEditView):
    fields = (
        'trash_time_unit', 'trash_time_period', 'delete_time_unit',
        'delete_time_period', 'document_stub_pruning_enabled',
        'document_stub_expiration_interval'
    )
    fieldsets = (
        (
            _('Trashing'), {
                'fields': ('trash_time_unit', 'trash_time_period'),
            }
        ), (
            _('Deletion'), {
                'fields': ('delete_time_unit', 'delete_time_period')
            }
        ), (
            _('Stub pruning'), {
                'fields': (
                    'document_stub_pruning_enabled',
                    'document_stub_expiration_interval'
                )
            }
        )
    )
    model = DocumentType
    object_permission = permission_document_type_edit
    pk_url_kwarg = 'document_type_id'
    post_action_redirect = reverse_lazy(
        viewname='documents:document_type_list'
    )
    view_icon = icon_document_type_retention_policies

    def get_extra_context(self):
        return {
            'object': self.object,
            'title': _(
                'Retention policies for document type: %s'
            ) % self.object
        }

    def get_instance_extra_data(self):
        return {
            '_event_actor': self.request.user
        }
