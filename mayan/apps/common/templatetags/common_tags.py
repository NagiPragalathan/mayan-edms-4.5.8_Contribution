import logging

from django.template import Library
from django.utils.encoding import force_text

import mayan

from ..classes import MissingItem
from ..settings import setting_project_title
from ..utils import return_attrib

logger = logging.getLogger(name=__name__)
register = Library()


@register.simple_tag
def common_get_missing_items():
    return MissingItem.get_missing()


@register.simple_tag
def common_get_object_verbose_name(obj):
    try:
        return obj._meta.verbose_name
    except AttributeError:
        try:
            return obj.verbose_name
        except AttributeError:
            if isinstance(obj, str):
                return ''
            else:
                return type(obj)


@register.simple_tag
def common_get_project_title():
    if setting_project_title.value:
        return '{} ({})'.format(mayan.__title__, setting_project_title.value)
    else:
        return mayan.__title__


@register.filter
def common_get_type(value):
    return force_text(s=type(value))


@register.filter
def common_object_property(value, arg):
    return return_attrib(value, arg)


@register.simple_tag
def common_project_information(attribute_name):
    return getattr(mayan, attribute_name)
