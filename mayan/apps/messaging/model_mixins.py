from django.utils.translation import ugettext_lazy as _

from bleach import Cleaner
from bleach.linkifier import LinkifyFilter

from mayan.apps.templating.classes import Template


class MessageBusinessLogicMixin:
    def get_label(self):
        return Template(
            template_string='{{ instance.date_time }} @{{ instance.sender_object }} "{{ instance.subject }}"'
        ).render(
            context={'instance': self}
        )
    get_label.short_description = _('Label')

    def get_rendered_body(self):
        cleaner = Cleaner(
            filters=[LinkifyFilter]
        )

        template = Template(
            template_string=cleaner.clean(text=self.body)
        )
        return template.render(
            context={'message': self}
        )

    def mark_read(self, user):
        self._event_actor = user
        self.read = True
        self.save(
            update_fields=('read',)
        )

    def mark_unread(self, user):
        self._event_actor = user
        self.read = False
        self.save(
            update_fields=('read',)
        )
