class OwnerPlusFilteredQuerysetAPIViewMixin:
    def filter_queryset(self, queryset):
        queryset_user_owned = queryset.filter(user=self.request.user)

        queryset_filtered = super().filter_queryset(queryset=queryset)

        queryset = queryset_user_owned | queryset_filtered
        return queryset.distinct()
