from django.utils.translation import ugettext_lazy as _

from mayan.apps.events.classes import EventTypeNamespace

namespace = EventTypeNamespace(
    label=_('Document exports'), name='document_exports'
)

event_document_version_exported = namespace.add_event_type(
    label=_('Document version exported'), name='document_version_exported'
)
