from django.contrib.messages.views import SuccessMessageMixin
from django.shortcuts import get_object_or_404
from django.views.generic import CreateView

from assignments.models import Exercise
from booking.models import Course


class UploadExercise(SuccessMessageMixin, CreateView):
    model = Exercise
    fields = ('file', )
    success_url = '/'
    success_message = '%(file)s successfully uploaded to %(course)s!'

    def get_form(self):
        form = super().get_form()
        form.fields['file'].widget.attrs['onchange'] = 'display_filename(this)'
        return form

    def form_valid(self, form):
        exercise = form.save(commit=False)
        exercise.student = self.request.user
        exercise.course = get_object_or_404(Course, slug=self.kwargs['slug'])
        exercise.save()
        # needed for the success message
        form.cleaned_data['course'] = exercise.course
        return super().form_valid(form)
