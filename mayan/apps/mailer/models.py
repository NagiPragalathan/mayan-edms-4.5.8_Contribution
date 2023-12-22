from django.db import models
from django.urls import reverse
from django.utils.translation import ugettext_lazy as _

from mayan.apps.backends.model_mixins import BackendModelMixin
from mayan.apps.events.decorators import method_event
from mayan.apps.events.event_managers import EventManagerSave

from .classes import NullBackend
from .events import event_profile_created, event_profile_edited
from .managers import UserMailerManager
from .model_mixins import UserMailerBusinessLogicMixin


class UserMailer(
    BackendModelMixin, UserMailerBusinessLogicMixin, models.Model
):
    """
    This model is used to create mailing profiles that can be used from inside
    the system. These profiles differ from the system mailing profile in that
    they can be created at runtime and can be assigned ACLs to restrict
    their use.
    """
    _backend_model_null_backend = NullBackend

    label = models.CharField(
        help_text=_('A short text describing the mailing profile.'),
        max_length=128, unique=True, verbose_name=_('Label')
    )
    default = models.BooleanField(
        default=True, help_text=_(
            'If default, this mailing profile will be pre-selected on the '
            'document mailing form.'
        ), verbose_name=_('Default')
    )
    enabled = models.BooleanField(
        default=True, verbose_name=_('Enabled')
    )

    objects = UserMailerManager()

    class Meta:
        ordering = ('label',)
        verbose_name = _('Mailing profile')
        verbose_name_plural = _('Mailing profiles')

    def __str__(self):
        return self.label

    def get_absolute_url(self):
        return reverse(viewname='mailer:user_mailer_list')

    def natural_key(self):
        return (self.label,)

    @method_event(
        event_manager_class=EventManagerSave,
        created={
            'event': event_profile_created,
            'target': 'self'
        },
        edited={
            'event': event_profile_edited,
            'target': 'self'
        }
    )
    def save(self, *args, **kwargs):
        if self.default:
            UserMailer.objects.select_for_update().exclude(
                pk=self.pk
            ).update(default=False)

        return super().save(*args, **kwargs)
