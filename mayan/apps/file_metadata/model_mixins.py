from django.utils.functional import cached_property
from django.utils.module_loading import import_string
from django.utils.translation import ugettext_lazy as _


class DocumentFileDriverEntryBusinessLogicMixin:
    def get_attribute_count(self):
        return self.entries.count()
    get_attribute_count.short_description = _('Attribute count')


class StoredDriverBusinessLogicMixin:
    @cached_property
    def driver_class(self):
        return import_string(dotted_path=self.driver_path)

    @cached_property
    def driver_label(self):
        return self.driver_class.label
