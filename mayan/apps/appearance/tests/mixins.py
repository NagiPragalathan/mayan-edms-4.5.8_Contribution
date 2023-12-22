from mayan.apps.testing.tests.mixins import TestMixinObjectCreationTrack

from ..models import Theme

from .literals import TEST_THEME_LABEL, TEST_THEME_LABEL_EDITED


class ThemeTestMixin(TestMixinObjectCreationTrack):
    _test_object_model = Theme
    _test_object_name = '_test_theme'

    def _create_test_theme(self):
        self._test_theme = Theme.objects.create(
            label=TEST_THEME_LABEL
        )

    def _edit_test_theme(self):
        self._test_theme.label = TEST_THEME_LABEL_EDITED
        self._test_theme.save()


class ThemeViewTestMixin(ThemeTestMixin):
    def _request_test_theme_create_view(self):
        self._test_object_track()

        response = self.post(
            viewname='appearance:theme_create', data={
                'label': TEST_THEME_LABEL,
            }
        )

        self._test_object_set()

        return response

    def _request_test_theme_delete_view(self):
        return self.post(
            viewname='appearance:theme_delete', kwargs={
                'theme_id': self._test_theme.pk
            }
        )

    def _request_test_theme_edit_view(self):
        return self.post(
            viewname='appearance:theme_edit', kwargs={
                'theme_id': self._test_theme.pk
            }, data={
                'label': TEST_THEME_LABEL_EDITED,
            }
        )

    def _request_test_theme_list_view(self):
        return self.get(viewname='appearance:theme_list')


class UserThemeSettingsViewTestMixin(ThemeTestMixin):
    def _request_test_current_user_theme_settings_detail_view(self):
        return self._request_test_user_theme_settings_detail_view(
            user=self._test_case_user
        )

    def _request_test_current_user_theme_settings_edit_view(self):
        return self._request_test_user_theme_settings_edit_view(
            user=self._test_case_user
        )

    def _request_test_super_user_theme_settings_detail_view(self):
        return self._request_test_user_theme_settings_detail_view(
            user=self._test_super_user
        )

    def _request_test_super_user_theme_settings_edit_view(self):
        return self._request_test_user_theme_settings_edit_view(
            user=self._test_super_user
        )

    def _request_test_user_theme_settings_detail_view(self, user=None):
        user = user or self._test_user

        return self.get(
            viewname='appearance:user_theme_settings_detail', kwargs={
                'user_id': user.pk
            }
        )

    def _request_test_user_theme_settings_edit_view(self, user=None):
        user = user or self._test_user

        return self.post(
            viewname='appearance:user_theme_settings_edit', kwargs={
                'user_id': user.pk
            }, data={
                'theme': self._test_theme.pk
            }
        )
