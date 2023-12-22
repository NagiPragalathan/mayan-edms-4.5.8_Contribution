from mayan.apps.events.decorators import method_event
from mayan.apps.events.event_managers import EventManagerMethodAfter

from .events import event_credential_used


class StoredCredentialBusinessLogicMixin:
    @method_event(
        event_manager_class=EventManagerMethodAfter,
        event=event_credential_used,
        target='self'
    )
    def get_backend_data(self):
        obj = super().get_backend_data()
        backend_class = self.get_backend_class()

        if hasattr(backend_class, 'post_processing'):
            obj = backend_class.post_processing(obj=obj)

        return obj
