from django.conf import settings
from django.core.exceptions import PermissionDenied
from django.shortcuts import redirect
from django.views.generic import TemplateView


class Home(TemplateView):
    template_name = 'itsBooking/index.html'


def populate_db(request):
    if settings.DEBUG:
        from . import populate_db
        return redirect('/')
    raise PermissionDenied()
