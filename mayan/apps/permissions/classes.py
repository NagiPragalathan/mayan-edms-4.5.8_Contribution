import itertools
import logging

from django.apps import apps
from django.core.exceptions import PermissionDenied
from django.db.utils import OperationalError, ProgrammingError
from django.utils.functional import cached_property
from django.utils.translation import ugettext_lazy as _

from mayan.apps.common.class_mixins import AppsModuleLoaderMixin
from mayan.apps.common.collections import ClassCollection

logger = logging.getLogger(name=__name__)


class PermissionNamespace:
    _registry = {}

    @classmethod
    def all(cls):
        return cls._registry.values()

    @classmethod
    def get(cls, name):
        return cls._registry[name]

    def __init__(self, name, label):
        self.name = name
        self.label = label
        self.permissions = []
        self.__class__._registry[name] = self

    def __str__(self):
        return str(self.label)

    def add_permission(self, name, label):
        permission = Permission(namespace=self, name=name, label=label)
        self.permissions.append(permission)
        return permission


class Permission(AppsModuleLoaderMixin):
    _imported_app = []
    _loader_module_name = 'permissions'
    _registry = {}

    @classmethod
    def all(cls):
        # Return sorted permissions by namespace.name
        return PermissionCollection(
            sorted(
                cls._registry.values(), key=lambda x: x.namespace.name
            )
        )

    @classmethod
    def check_user_permissions(cls, permissions, user):
        for permission in permissions:
            if permission.stored_permission.user_has_this(user=user):
                return True

        logger.debug(
            'User "%s" does not have permissions "%s"', user, permissions
        )
        raise PermissionDenied(
            _('Insufficient permissions.')
        )

    @classmethod
    def get(cls, pk):
        return cls._registry[pk]

    @classmethod
    def get_choices(cls):
        results = PermissionCollection()

        for namespace, permissions in itertools.groupby(cls.all(), lambda entry: entry.namespace):
            permission_options = [
                (permission.pk, permission) for permission in permissions
            ]
            results.append(
                (namespace, permission_options)
            )

        return results

    @classmethod
    def load_modules(cls):
        super().load_modules()

        # Prime cache for all permissions.
        for permission in cls.all():
            permission.stored_permission

    @classmethod
    def invalidate_cache(cls):
        for permission in cls.all():
            try:
                del permission.stored_permission
            except AttributeError:
                """Stored permission was not cached."""

    def __init__(self, namespace, name, label):
        self.namespace = namespace
        self.name = name
        self.label = label
        self.pk = self.get_pk()
        self.__class__._registry[self.pk] = self

    def __repr__(self):
        return self.pk

    def __str__(self):
        return str(self.label)

    def get_pk(self):
        return '{}.{}'.format(self.namespace.name, self.name)

    @cached_property
    def stored_permission(self):
        StoredPermission = apps.get_model(
            app_label='permissions', model_name='StoredPermission'
        )

        try:
            stored_permission, created = StoredPermission.objects.get_or_create(
                name=self.name, namespace=self.namespace.name
            )

            return stored_permission
        except (OperationalError, ProgrammingError):
            """
            This error is expected when trying to initialize the
            stored permissions during the initial creation of the
            database. Can be safely ignore under that situation.
            """


class PermissionCollection(ClassCollection):
    klass = Permission
