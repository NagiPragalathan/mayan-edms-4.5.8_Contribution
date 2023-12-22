from mayan.apps.testing.tests.base import BaseTestCase

from .literals import (
    MAILER_BACKEND_DJANGO_FILE_PATH, MAILER_BACKEND_DJANGO_SMTP_PATH,
    TEST_DJANGO_FILE_PATH
)
from .mixins import MailerTestMixin


class DjangoMailerBackendTestCase(MailerTestMixin, BaseTestCase):
    _test_mailer_backend_path = MAILER_BACKEND_DJANGO_SMTP_PATH

    def test_mailer_connection_kwargs(self):
        self._create_test_user_mailer(
            extra_backend_data={
                'host': '127.0.0.1',
                'port': '999',
                'stored_credential_id': self._test_stored_credential.pk
            }
        )

        backend_instance = self._test_user_mailer.get_backend_instance()
        connection_kwargs = backend_instance.get_connection_kwargs()

        self.assertEqual(
            connection_kwargs['password'],
            self._test_stored_credential_backend_data['password']
        )
        self.assertEqual(
            connection_kwargs['username'],
            self._test_stored_credential_backend_data['username']
        )


class DjangoFileMailerTestCase(MailerTestMixin, BaseTestCase):
    _test_mailer_backend_path = MAILER_BACKEND_DJANGO_FILE_PATH

    def test_mailer_connection_kwargs(self):
        self._create_test_user_mailer(
            extra_backend_data={'file_path': TEST_DJANGO_FILE_PATH}
        )

        backend_instance = self._test_user_mailer.get_backend_instance()
        connection_kwargs = backend_instance.get_connection_kwargs()

        self.assertEqual(
            connection_kwargs['file_path'], TEST_DJANGO_FILE_PATH
        )
