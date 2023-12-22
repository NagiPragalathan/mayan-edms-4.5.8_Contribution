from django.utils.translation import ugettext_lazy as _

from rest_framework import serializers as rest_framework_serializers
from rest_framework.fields import (  # NOQA
    BooleanField, CharField, ChoiceField, DateField, DateTimeField,
    DecimalField, DictField, DurationField, EmailField, Field, FileField,
    FilePathField, FloatField, HiddenField, HStoreField, IPAddressField,
    ImageField, IntegerField, JSONField, ListField, ModelField,
    MultipleChoiceField, ReadOnlyField, RegexField, SerializerMethodField,
    SlugField, TimeField, URLField, UUIDField
)
from rest_framework.serializers import (
    HyperlinkedModelSerializer as RESTFrameworkHyperlinkedModelSerializer,
    ModelSerializer as RESTFrameworkModelSerializer
)
from rest_framework.relations import (  # NOQA
    HyperlinkedIdentityField, HyperlinkedRelatedField, ManyRelatedField,
    PrimaryKeyRelatedField, RelatedField, SlugRelatedField,
    StringRelatedField
)
from rest_framework.reverse import reverse

from .classes import BatchRequestCollection
from .serializer_mixins import (
    CreateOnlyFieldSerializerMixin, DynamicFieldListSerializerMixin
)


class Serializer(
    DynamicFieldListSerializerMixin, rest_framework_serializers.Serializer
):
    """Serializer subclass to add Mayan specific mixins."""


class BatchAPIRequestResponseSerializer(Serializer):
    content = CharField(
        label=_('Content'), read_only=True
    )
    data = JSONField(
        label=_('Data'), read_only=True
    )
    headers = DictField(
        label=_('Headers'), read_only=True
    )
    name = CharField(
        label=_('Name'), read_only=True
    )
    status_code = IntegerField(
        label=_('Status code'), read_only=True
    )
    requests = JSONField(
        label=_('Requests'), style={'base_template': 'textarea.html'},
        write_only=True
    )

    def validate(self, data):
        try:
            BatchRequestCollection(
                request_list=data['requests']
            )
        except Exception as exception:
            raise rest_framework_serializers.ValidationError(
                'Error validating requests; {}'.format(exception)
            )

        return data


class BlankSerializer(Serializer):
    """Serializer for the object action API view."""


class EndpointSerializer(Serializer):
    label = CharField(
        label=_('Label'), read_only=True
    )
    url = SerializerMethodField(
        label=_('URL')
    )

    def get_url(self, instance):
        if instance.viewname:
            return reverse(
                kwargs=instance.kwargs, viewname=instance.viewname,
                request=self.context['request'],
                format=self.context['format']
            )


class HyperlinkedModelSerializer(
    CreateOnlyFieldSerializerMixin, DynamicFieldListSerializerMixin,
    RESTFrameworkHyperlinkedModelSerializer
):
    """HyperlinkedModelSerializer subclass to add Mayan specific mixins."""


class ModelSerializer(
    CreateOnlyFieldSerializerMixin, DynamicFieldListSerializerMixin,
    RESTFrameworkModelSerializer
):
    """ModelSerializer subclass to add Mayan specific mixins."""


class ProjectInformationSerializer(Serializer):
    __author__ = CharField(
        label=_('Author'), read_only=True
    )
    __author_email__ = CharField(
        label=_('Author email'), read_only=True
    )
    __build__ = CharField(
        label=_('Build'), read_only=True
    )
    __build_string__ = CharField(
        label=_('Build string'), read_only=True
    )
    __copyright__ = CharField(
        label=_('Copyright'), read_only=True
    )
    __description__ = CharField(
        label=_('Description'), read_only=True
    )
    __django_version__ = CharField(
        label=_('Django version'), read_only=True
    )
    __license__ = CharField(
        label=_('License'), read_only=True
    )
    __title__ = CharField(
        label=_('Title'), read_only=True
    )
    __version__ = CharField(
        label=_('Version'), read_only=True
    )
    __website__ = CharField(
        label=_('Website'), read_only=True
    )
