import logging

import sentry_sdk
from sentry_sdk.integrations.celery import CeleryIntegration
from sentry_sdk.integrations.django import DjangoIntegration
from sentry_sdk.integrations.redis import RedisIntegration

from django.conf.urls import url
from django.utils.translation import ugettext_lazy as _

import mayan
from mayan.apps.appearance.classes import Icon
from mayan.apps.common.utils import any_to_bool
from mayan.apps.navigation.classes import Link

from .classes import ClientBackend
from .permissions import permission_test_trigger

logger = logging.getLogger(name=__name__)


class ClientBackendSentry(ClientBackend):
    _url_namespace = 'sentry'

    def get_links(self):
        icon_sentry_debug = Icon(
            driver_name='fontawesome', symbol='bug'
        )

        return (
            Link(
                icon=icon_sentry_debug,
                permissions=(permission_test_trigger,),
                text=_('Sentry test error'),
                view='platform:sentry_debug',
            ),
        )

    def get_url_patterns(self):
        def view_trigger_error(request):
            1 / 0

        return [
            url(
                regex=r'^debug/$', name='sentry_debug',
                view=view_trigger_error
            )
        ]

    def launch(self):
        kwargs = self.setup_arguments()

        kwargs['integrations'] = (
            CeleryIntegration(), DjangoIntegration(), RedisIntegration()
        )

        logger.debug('cleaned arguments: %s', kwargs)

        sentry_instance = sentry_sdk.init(**kwargs)

        logger.debug('client options: %s', sentry_instance._client.options)

    def setup_arguments(self):
        logger.debug('raw arguments: %s', self.kwargs)

        # https://docs.sentry.io/platforms/python/configuration/options/
        options = {}

        # Common Options
        options['dsn'] = self.kwargs['dsn']

        options['debug'] = any_to_bool(
            value=self.kwargs.get('debug', False)
        )

        options['release'] = mayan.__build_string__

        options['environment'] = self.kwargs.get('environment')

        options['sample_rate'] = float(
            self.kwargs.get('sample_rate', 1.0)
        )

        options['max_breadcrumbs'] = int(
            self.kwargs.get('max_breadcrumbs', 100)
        )

        options['attach_stacktrace'] = any_to_bool(
            value=self.kwargs.get('attach_stacktrace', False)
        )

        options['send_default_pii'] = any_to_bool(
            value=self.kwargs.get('send_default_pii', True)
        )

        options['server_name'] = self.kwargs.get('server_name')

        options['with_locals'] = any_to_bool(
            value=self.kwargs.get('with_locals', True)
        )

        # Transport Options
        options['transport'] = self.kwargs.get('transport')

        options['http_proxy'] = self.kwargs.get('http_proxy')

        options['https_proxy'] = self.kwargs.get('https_proxy')

        options['shutdown_timeout'] = int(
            self.kwargs.get('shutdown_timeout', 2)
        )

        # Tracing Options
        options['traces_sample_rate'] = float(
            self.kwargs.get('traces_sample_rate', 0.005)
        )

        return options
