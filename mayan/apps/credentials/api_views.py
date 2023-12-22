from mayan.apps.rest_api import generics

from .models import StoredCredential
from .permissions import (
    permission_credential_create, permission_credential_delete,
    permission_credential_edit, permission_credential_view
)
from .serializers import StoredCredentialSerializer


class APIStoredCredentialListView(generics.ListCreateAPIView):
    """
    get: Returns a list of all the import setups.
    post: Create a new import setup.
    """
    mayan_object_permissions = {
        'GET': (permission_credential_view,)
    }
    mayan_view_permissions = {
        'POST': (permission_credential_create,)
    }
    serializer_class = StoredCredentialSerializer
    source_queryset = StoredCredential.objects.all()

    def get_instance_extra_data(self):
        return {
            '_event_actor': self.request.user
        }


class APIStoredCredentialDetailView(generics.RetrieveUpdateDestroyAPIView):
    """
    delete: Delete the selected import setup.
    get: Return the details of the selected import setup.
    patch: Edit the selected import setup.
    put: Edit the selected import setup.
    """
    lookup_url_kwarg = 'credential_id'
    mayan_object_permissions = {
        'DELETE': (permission_credential_delete,),
        'GET': (permission_credential_view,),
        'PATCH': (permission_credential_edit,),
        'PUT': (permission_credential_edit,)
    }
    serializer_class = StoredCredentialSerializer
    source_queryset = StoredCredential.objects.all()

    def get_instance_extra_data(self):
        return {
            '_event_actor': self.request.user
        }
