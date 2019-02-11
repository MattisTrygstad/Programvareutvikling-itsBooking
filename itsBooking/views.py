from django.conf import settings
from django.contrib import messages
from django.contrib.auth.forms import AuthenticationForm
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.views import LoginView, LogoutView
from django.contrib.messages.views import SuccessMessageMixin
from django.core.exceptions import PermissionDenied
from django.shortcuts import redirect
from django.views.generic import TemplateView

from booking.models import Course


class Home(TemplateView, LoginRequiredMixin):
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

    def get_next_page(self):
        next_page = super(LogoutView, self).get_next_page()
        messages.add_message(
            self.request, messages.SUCCESS,
            'Utlogging vellykket!'
        )
        return next_page


def populate_db(request):
    if settings.DEBUG:
        from . import populate_db
        messages.success(request, 'Database flushed and populated successfully!')
        return redirect('/')
    raise PermissionDenied()
