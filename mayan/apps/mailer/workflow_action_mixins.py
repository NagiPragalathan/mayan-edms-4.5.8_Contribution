from django.utils.translation import ugettext_lazy as _

from .models import UserMailer
from .permissions import permission_user_mailer_use


class ObjectEmailActionMixin:
    form_field_widgets = {
        'body': {
            'class': 'django.forms.widgets.Textarea', 'kwargs': {}
        }
    }
    form_fields = {
        'recipient': {
            'label': _('Recipient'),
            'class': 'django.forms.CharField', 'kwargs': {
                'help_text': _(
                    'Email address of the recipient. Can be multiple '
                    'addresses separated by comma or semicolon. A template '
                    'can be used to reference properties of the document.'
                ),
                'required': True
            }
        },
        'cc': {
            'label': _('CC'),
            'class': 'django.forms.CharField', 'kwargs': {
                'help_text': _(
                    'Address used in the "Bcc" header when sending the '
                    'email. Can be multiple addresses '
                    'separated by comma or semicolon. A template can be '
                    'used to reference properties of the document.'
                ),
                'required': False
            }
        },
        'bcc': {
            'label': _('BCC'),
            'class': 'django.forms.CharField', 'kwargs': {
                'help_text': _(
                    'Address used in the "Bcc" header when sending the '
                    'email. Can be multiple addresses '
                    'separated by comma or semicolon. A template can be '
                    'used to reference properties of the document.'
                ),
                'required': False
            }
        },
        'reply_to': {
            'label': _('Reply to'),
            'class': 'django.forms.CharField', 'kwargs': {
                'help_text': _(
                    'Address used in the "Reply-To" header when sending '
                    'the email. Can be multiple addresses separated by '
                    'comma or semicolon. A template can be used to '
                    'reference properties of the document.'
                ),
                'required': False
            }
        },
        'subject': {
            'label': _('Subject'),
            'class': 'django.forms.CharField', 'kwargs': {
                'help_text': _(
                    'Subject of the email. Can be a string or a template.'
                ),
                'required': False
            }
        },
        'body': {
            'label': _('Body'),
            'class': 'django.forms.CharField', 'kwargs': {
                'help_text': _(
                    'Body of the email to send. Can be a string or '
                    'a template.'
                ),
                'required': False
            }
        },
        'attachment': {
            'label': _('Attachment'),
            'class': 'django.forms.BooleanField', 'default': False,
            'help_text': _(
                'Attach an object to the email.'
            ),
            'required': False
        }
    }
    label = _('Send object via email')
    permission = permission_user_mailer_use

    @classmethod
    def get_form_fields(cls, *args, **kwargs):
        fields = super().get_form_fields(*args, **kwargs)

        fields.update(
            {
                'mailing_profile': {
                    'class': 'mayan.apps.views.fields.FormFieldFilteredModelChoice',
                    'help_text': _(
                        'Mailing profile to use when sending the email.'
                    ),
                    'kwargs': {
                        'source_queryset': UserMailer.objects.filter(enabled=True),
                        'permission': cls.permission
                    },
                    'label': _('Mailing profile'),
                    'required': True
                }
            }
        )

        return fields

    @classmethod
    def get_form_fieldsets(cls):
        fieldsets = super().get_form_fieldsets()

        fieldsets += (
            (
                _('Mailing profile'), {
                    'fields': ('mailing_profile',)
                }
            ), (
                _('Parties'), {
                    'fields': ('recipient', 'cc', 'bcc', 'reply_to')
                },
            ), (
                _('Content'), {
                    'fields': ('subject', 'attachment', 'body')
                },
            )
        )
        return fieldsets

    def execute(self, context):
        user_mailer = self.get_user_mailer()
        user_mailer.send_object(
            **self.get_execute_data(context=context)
        )

    def get_execute_data(self, context):
        recipient = self.render_field(
            field_name='recipient', context=context
        )
        cc = self.render_field(
            field_name='cc', context=context
        )
        bcc = self.render_field(
            field_name='bcc', context=context
        )
        reply_to = self.render_field(
            field_name='reply_to', context=context
        )
        subject = self.render_field(
            field_name='subject', context=context
        )
        body = self.render_field(
            field_name='body', context=context
        )

        kwargs = {
            'bcc': bcc, 'body': body, 'cc': cc,
            'obj': self.get_object(context=context), 'reply_to': reply_to,
            'subject': subject, 'to': recipient
        }

        return kwargs

    def get_object(self, context):
        return NotImplementedError

    def get_user_mailer(self):
        return UserMailer.objects.get(
            pk=self.kwargs['mailing_profile']
        )
