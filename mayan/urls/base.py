__all__ = ('urlpatterns',)


from django.urls import path
from .views import simple_string_view

urlpatterns = [
    path('simple/', simple_string_view, name='simple_string_view'),
]
