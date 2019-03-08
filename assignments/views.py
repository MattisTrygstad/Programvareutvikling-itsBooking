from django.contrib.auth.mixins import UserPassesTestMixin
from django.contrib.auth.models import Group
from django.contrib.messages.views import SuccessMessageMixin
from django.db.models import Q
from django.shortcuts import get_object_or_404
from django.views.generic import CreateView, ListView

from assignments.forms import ExerciseReviewForm
from assignments.models import Exercise
from booking.models import Course


class ExerciseList(UserPassesTestMixin, ListView):
    template_name = 'assignments/exercise_list.html'

    def get_queryset(self):
        return Exercise.objects.filter(course__slug=self.kwargs['slug'])

    def get_context_data(self, **kwargs):
        context = super().get_context_data()
        course = get_object_or_404(Course, slug=self.kwargs['slug'])
        context.update({'course': course, 'form': ExerciseReviewForm()})
        return context

    def test_func(self):
        allowed_groups = Group.objects.filter(Q(name='course_coordinators') | Q(name='assistants'))
        usr_groups = self.request.user.groups.all()
        return any(g in allowed_groups for g in usr_groups)


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
