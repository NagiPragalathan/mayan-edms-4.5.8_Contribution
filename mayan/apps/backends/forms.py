import json

from django import forms as django_forms
from django.db.models import Model
from django.db.models.query import QuerySet
from django.forms.models import ModelFormMetaclass

from mayan.apps.views.forms import DynamicModelForm


class BackendDynamicFormMetaclass(ModelFormMetaclass):
    def __new__(mcs, name, bases, attrs):
        new_class = super(BackendDynamicFormMetaclass, mcs).__new__(
            mcs=mcs, name=name, bases=bases, attrs=attrs
        )

        if new_class._meta.fields:
            new_class._meta.fields += ('backend_data',)
            widgets = getattr(
                new_class._meta, 'widgets', {}
            ) or {}
            widgets['backend_data'] = django_forms.widgets.HiddenInput
            new_class._meta.widgets = widgets

        return new_class


class FormDynamicModelBackend(
    DynamicModelForm, metaclass=BackendDynamicFormMetaclass
):
    widgets = {'backend_data': django_forms.widgets.HiddenInput}

    def __init__(self, backend_path=None, user=None, *args, **kwargs):
        self.backend_path = backend_path
        # For the filtered fields reload method.
        self.user = user

        super().__init__(*args, **kwargs)

        backend_data = self.instance.get_backend_data()

        if backend_data:
            for field_name in self.get_backend_fields():
                self.fields[field_name].initial = backend_data.get(
                    field_name, None
                )

        # TODO: REMOVE this and move it to the specific app form subclass.
        # Updated filtered fields.
        for field in self.fields:
            if hasattr(self.fields[field], 'reload'):
                self.fields[field].user = self.user
                self.fields[field].reload()

    def clean(self):
        data = super().clean()

        # Consolidate the dynamic fields into a single JSON field called
        # 'backend_data'.
        backend_data = {}

        for field_name, field_data in self.schema['fields'].items():
            backend_data[field_name] = data.pop(
                field_name, field_data.get('default', None)
            )
            if isinstance(backend_data[field_name], QuerySet):
                # Flatten the queryset to a list of ids.
                backend_data[field_name] = list(
                    backend_data[field_name].values_list('id', flat=True)
                )
            elif isinstance(backend_data[field_name], Model):
                # Store only the ID of a model instance.
                backend_data[field_name] = backend_data[field_name].pk

        data['backend_data'] = json.dumps(obj=backend_data)

        return data

    def get_backend_fields(self):
        backend_class = self.instance.get_backend_class()
        return backend_class.get_form_fields()
