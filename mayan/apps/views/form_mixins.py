from django import forms as django_forms
from django.core.exceptions import ImproperlyConfigured
from django.utils.module_loading import import_string


class FormMixinDynamicFields:
    def __init__(self, schema, *args, **kwargs):
        self.schema = schema

        super().__init__(*args, **kwargs)

        self.fieldsets = self.schema.get(
            'fieldsets', ()
        )
        self.fieldset_exclude_list = self.schema.get(
            'fieldset_exclude_list', ()
        )

        widgets = self.schema.get(
            'widgets', {}
        )

        field_order = self.get_field_order()

        for field_name in field_order:
            field_data = self.schema['fields'][field_name]
            field_class = import_string(
                dotted_path=field_data['class']
            )
            kwargs = {
                'label': field_data['label'],
                'required': field_data.get('required', True),
                'initial': field_data.get('default', None),
                'help_text': field_data.get('help_text')
            }

            widget = widgets.get(field_name)
            if widget:
                kwargs['widget'] = import_string(
                    dotted_path=widget['class']
                )(
                    **widget.get(
                        'kwargs', {}
                    )
                )

            kwargs.update(
                field_data.get(
                    'kwargs', {}
                )
            )
            self.fields[field_name] = field_class(**kwargs)

    def get_field_order(self):
        return self.schema.get(
            'field_order', self.schema['fields'].keys()
        )

    @property
    def media(self):
        """
        Append the media of the dynamic fields to the normal fields' media.
        """
        media = super().media
        media += django_forms.Media(
            **self.schema.get(
                'media', {}
            )
        )
        return media


class FormMixinFieldsets:
    fieldset_exclude_list = None
    fieldsets = None

    def get_fieldset_exclude_list(self):
        return self.fieldset_exclude_list or ()

    def get_fieldsets(self):
        if self.fieldsets:
            fieldsets_field_list = []
            for fieldset, data in self.fieldsets:
                fieldsets_field_list.extend(
                    data['fields']
                )

            set_fields = set(self.fields)
            set_fieldsets = set(fieldsets_field_list)

            fieldset_exclude_list = self.get_fieldset_exclude_list()

            if fieldset_exclude_list:
                set_fields -= set(fieldset_exclude_list)
                set_fieldsets -= set(fieldset_exclude_list)

            if set_fields != set_fieldsets:
                raise ImproperlyConfigured(
                    'Mismatch fieldset fields: {fields} in form `{form}`'.format(
                        fields=', '.join(
                            set_fields.symmetric_difference(set_fieldsets)
                        ), form=self.__class__.__name__
                    )
                )

            return self.fieldsets
        else:
            return (
                (
                    None, {
                        'fields': tuple(self.fields)
                    }
                ),
            )
