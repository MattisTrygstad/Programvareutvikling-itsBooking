from django import forms
from django.contrib.messages.views import SuccessMessageMixin
from django.shortcuts import render
from django.views.generic import CreateView

from assignments.models import Exercise


class UploadExercise(SuccessMessageMixin, CreateView):
    model = Exercise
    fields = ('file', )
    success_url = '/'
    success_message = 'Exercise file %(file)s successfully uploaded to %(course)s!'

    def get_form(self):
        form = super().get_form()
        form.fields['file'].widget.attrs['onchange'] = 'display_filename(this)'
        return form

