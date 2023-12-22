from django.utils.translation import ugettext_lazy as _

from .classes import Layer
from .icons import icon_layer_decorations, icon_layer_transformation
from .permissions import (
    permission_transformation_create, permission_transformation_delete,
    permission_transformation_edit, permission_transformation_view
)

layer_decorations = Layer(
    empty_results_text=_(
        'Decorations are visual elements that add contextual information to '
        'images.'
    ), icon=icon_layer_decorations, label=_('Decorations'),
    name='decorations', order=10, permissions={
        'create': permission_transformation_create,
        'delete': permission_transformation_delete,
        'edit': permission_transformation_edit,
        'select': permission_transformation_create,
        'view': permission_transformation_view
    }
)

layer_saved_transformations = Layer(
    default=True, icon=icon_layer_transformation, label=_(
        'Saved transformations'
    ), name='saved_transformations', order=100, permissions={
        'create': permission_transformation_create,
        'delete': permission_transformation_delete,
        'edit': permission_transformation_edit,
        'select': permission_transformation_create,
        'view': permission_transformation_view
    }
)
