from django.conf import settings
from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.views import LoginView, LogoutView
from django.contrib.messages.views import SuccessMessageMixin
from django.core.exceptions import PermissionDenied
from django.views.generic import TemplateView

from booking.models import Course


class Home(LoginRequiredMixin, TemplateView):
    template_name = 'itsBooking/index.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data()
        context['course_list'] = Course.objects.all()
        return context


class LoginView(SuccessMessageMixin, LoginView):
    template_name = 'itsBooking/login.html'
    success_message = 'Innlogging vellykket!'

    def get_form(self):
        form = super().get_form()
        form.fields['username'].widget.attrs['class'] = 'uk-input uk-form-large'
        form.fields['password'].widget.attrs['class'] = 'uk-input uk-form-large'
        return form


class LogoutView(SuccessMessageMixin, LogoutView):
    def get(self, request):
        return logout(request)


def populate_db(request):
    if settings.DEBUG:
        from . import populate_db
        messages.success(request, 'Database flushed and populated successfully!')
        return LogoutView.as_view()(request)
    raise PermissionDenied()
