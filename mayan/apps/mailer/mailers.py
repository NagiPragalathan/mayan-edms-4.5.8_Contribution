from django.utils.translation import ugettext_lazy as _

from .classes import MailerBackendBaseEmail, MailerBackendCredentials


class DjangoSMTP(MailerBackendCredentials):
    """
    Backend that wraps Django's SMTP backend
    """
    class_path = 'django.core.mail.backends.smtp.EmailBackend'
    label = _('Django SMTP backend')

    @classmethod
    def get_form_fields(cls):
        fields = super().get_form_fields()

        fields.update(
            {
                'host': {
                    'label': _('Host'),
                    'class': 'django.forms.CharField',
                    'default': 'localhost',
                    'help_text': _('The host to use for sending email.'),
                    'kwargs': {
                        'max_length': 48
                    }, 'required': True
                }, 'port': {
                    'label': _('Port'),
                    'class': 'django.forms.IntegerField', 'default': 25,
                    'help_text': _('Port to use for the SMTP server.'),
                    'required': True
                }, 'use_tls': {
                    'label': _('Use TLS'),
                    'class': 'django.forms.BooleanField', 'default': False,
                    'help_text': _(
                        'Whether to use a TLS (secure) connection when '
                        'talking to the SMTP server. This is used for '
                        'explicit TLS connections, generally on port 587.'
                    ), 'required': False
                }, 'use_ssl': {
                    'label': _('Use SSL'),
                    'class': 'django.forms.BooleanField', 'default': False,
                    'help_text': _(
                        'Whether to use an implicit TLS (secure) connection '
                        'when talking to the SMTP server. In most email '
                        'documentation this type of TLS connection is '
                        'referred to as SSL. It is generally used on port '
                        '465. If you are experiencing problems, see the '
                        'explicit TLS setting "Use TLS". Note that '
                        '"Use TLS" and "Use SSL" are mutually exclusive, '
                        'so only set one of those settings to True.'
                    ), 'required': False
                }
            }
        )

        return fields

    @classmethod
    def get_form_fieldsets(cls):
        fieldsets = super().get_form_fieldsets()

        fieldsets += (
            (
                _('Server'), {
                    'fields': ('host', 'port', 'use_ssl', 'use_tls')
                }
            ),
        )

        return fieldsets

    def get_connection_kwargs(self):
        result = super().get_connection_kwargs()

        result.update(
            {
                'host': self.kwargs['host'],
                'port': self.kwargs['port'],
                'use_ssl': self.kwargs.get('use_ssl'),
                'use_tls': self.kwargs.get('use_tls')
            }
        )

        return result


class DjangoFileBased(MailerBackendBaseEmail):
    """
    Mailing backend that wraps Django's file based email backend
    """
    class_path = 'django.core.mail.backends.filebased.EmailBackend'
    label = _('Django file based backend')

    @classmethod
    def get_form_fields(cls):
        fields = super().get_form_fields()
        fields.update(
            {
                'file_path': {
                    'label': _('File path'),
                    'class': 'django.forms.CharField', 'kwargs': {
                        'max_length': 48
                    }
                }
            }
        )

        return fields

    @classmethod
    def get_form_fieldsets(cls):
        fieldsets = super().get_form_fieldsets()

        fieldsets += (
            (
                _('Storage'), {
                    'fields': ('file_path',)
                }
            ),
        )

        return fieldsets

    def get_connection_kwargs(self):
        result = super().get_connection_kwargs()

        result.update(
            {
                'file_path': self.kwargs['file_path']
            }
        )

        return result
