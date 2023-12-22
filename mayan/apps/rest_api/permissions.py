from django.core.exceptions import PermissionDenied

from rest_framework.permissions import BasePermission

from mayan.apps.acls.models import AccessControlList
from mayan.apps.permissions import Permission


class MayanPermission(BasePermission):
    def get_mayan_object_permissions(self, request, view):
        try:
            method_get_mayan_object_permissions = getattr(
                view, 'get_mayan_object_permissions'
            )
        except AttributeError:
            return getattr(
                view, 'mayan_object_permissions', {}
            ).get(request.method, None)
        else:
            return method_get_mayan_object_permissions(
                request=request, view=view
            )

    def get_mayan_view_permissions(self, request, view):
        try:
            method_get_mayan_view_permissions = getattr(
                view, 'get_mayan_view_permissions'
            )
        except AttributeError:
            return getattr(
                view, 'mayan_view_permissions', {}
            ).get(request.method, None)
        else:
            return method_get_mayan_view_permissions(
                request=request, view=view
            )

    def has_object_permission(self, request, view, obj):
        permissions = self.get_mayan_object_permissions(
            request=request, view=view
        )
        user = request.user

        if permissions:
            if user.is_authenticated:
                try:
                    AccessControlList.objects.check_access(
                        obj=obj, permissions=permissions,
                        user=user
                    )
                except PermissionDenied:
                    return False
                else:
                    return True
            else:
                return False
        else:
            return True

    def has_permission(self, request, view):
        permissions = self.get_mayan_view_permissions(
            request=request, view=view
        )
        user = request.user

        if permissions:
            if user.is_authenticated:
                try:
                    Permission.check_user_permissions(
                        permissions=permissions, user=user
                    )
                except PermissionDenied:
                    return False
                else:
                    return True
            else:
                return False
        else:
            return True
