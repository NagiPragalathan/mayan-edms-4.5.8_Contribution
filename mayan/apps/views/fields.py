from django import forms

from .field_mixins import (
    FormFieldMixinFilteredQueryset, ModelFieldMixinFilteredQuerySet
)


class FormFieldFilteredModelChoice(
    FormFieldMixinFilteredQueryset, forms.ChoiceField
):
    """Single selection filtered model choice field."""


class FormFieldFilteredModelChoiceMultiple(
    FormFieldMixinFilteredQueryset, forms.MultipleChoiceField
):
    """Multiole selection filtered model choice field."""


class ModelFormFieldFilteredModelChoice(
    ModelFieldMixinFilteredQuerySet, forms.ModelChoiceField
):
    """Single selection filtered model choice field."""


class ModelFormFieldFilteredModelMultipleChoice(
    ModelFieldMixinFilteredQuerySet, forms.ModelMultipleChoiceField
):
    """Multiple selection filtered model choice field."""
