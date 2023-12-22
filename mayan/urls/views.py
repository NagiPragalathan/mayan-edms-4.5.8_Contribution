from django.http import HttpResponse

def simple_string_view(request):
    """
    A simple Django view that returns a string.
    """
    return HttpResponse("Hello, this is a simple string response.")
