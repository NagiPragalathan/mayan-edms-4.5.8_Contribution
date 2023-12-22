import functools
import hashlib

from django.template.response import TemplateResponse
from django.template.utils import EngineHandler
from django.urls import reverse


class AJAXTemplate:
    _registry = {}

    @classmethod
    def all(cls, rendered=False, request=None):
        if not rendered:
            return cls._registry.values()
        else:
            result = []
            for template in cls._registry.values():
                result.append(
                    template.render(request=request)
                )
            return result

    @classmethod
    def get(cls, name):
        return cls._registry[name]

    def __init__(self, name, template_name, context=None):
        self.context = context or None
        self.name = name
        self.template_name = template_name
        self.__class__._registry[name] = self

    def get_absolute_url(self):
        return reverse(
            kwargs={'name': self.name}, viewname='rest_api:template-detail'
        )

    def render(self, request):
        result = TemplateResponse(
            context=self.context, request=request,
            template=self.template_name
        ).render()

        # Calculate the hash of the bytes version but return the unicode
        # version.
        self.html = result.rendered_content.replace('\n', '')
        self.hex_hash = hashlib.sha256(string=result.content).hexdigest()
        return self


class Template:
    @classmethod
    @functools.cache
    def get_backend(cls):
        engine_handler = EngineHandler(
            templates=(
                {
                    'BACKEND': 'django.template.backends.django.DjangoTemplates',
                    'OPTIONS': {
                        'builtins': [
                            'mathfilters.templatetags.mathfilters',
                            'mayan.apps.templating.templatetags.templating_tags'
                        ]
                    }
                },
            )
        )
        return engine_handler['django']

    def __init__(self, template_string):
        self._template = Template.get_backend().from_string(
            template_code=template_string
        )

    def render(self, context=None):
        if context is None:
            context = {}

        return self._template.render(context=context)
