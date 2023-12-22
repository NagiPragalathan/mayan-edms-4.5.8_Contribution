from mayan.apps.acls.models import AccessControlList


class OwnerPlusFilteredQuerysetViewMixin:
    def get_source_queryset(self):
        queryset = super().get_source_queryset()
        queryset_user = queryset.filter(user=self.request.user)

        queryset = queryset_user | AccessControlList.objects.restrict_queryset(
            permission=self.optional_object_permission,
            queryset=queryset, user=self.request.user
        )

        return queryset.distinct()
