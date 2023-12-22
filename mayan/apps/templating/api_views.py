from rest_framework.permissions import IsAuthenticated

from mayan.apps.rest_api import generics

from .classes import AJAXTemplate
from .serializers import AJAXTemplateSerializer


class APITemplateDetailView(generics.RetrieveAPIView):
    """
    Returns the selected partial template details.
    get: Retrieve the details of the partial template.
    """
    permission_classes = (IsAuthenticated,)
    serializer_class = AJAXTemplateSerializer

    def get_object(self):
        return AJAXTemplate.get(
            name=self.kwargs['name']
        ).render(
            request=self.request
        )


class APITemplateListView(generics.ListAPIView):
    """
    Returns a list of all the available templates.
    """
    permission_classes = (IsAuthenticated,)
    serializer_class = AJAXTemplateSerializer

    def get_source_queryset(self):
        return AJAXTemplate.all(
            rendered=True, request=self.request
        )
