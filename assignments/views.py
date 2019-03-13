from django.contrib import messages
from django.contrib.auth.mixins import UserPassesTestMixin
from django.contrib.auth.models import Group
from django.contrib.messages.views import SuccessMessageMixin
from django.db.models import Q
from django.http import HttpResponse, HttpResponseRedirect
from django.shortcuts import get_object_or_404
from django.urls import reverse
from django.views.generic import CreateView, ListView, UpdateView, TemplateView

from assignments.forms import ExerciseFeedbackForm
from assignments.models import Exercise
from booking.models import Course


class CourseExerciseList(UserPassesTestMixin, TemplateView):
    template_name = 'assignments/exercise_list.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data()
        course = get_object_or_404(Course, slug=self.kwargs['slug'])
        context.update({'course': course,
                        'form': ExerciseFeedbackForm(),
                        'exercise_list': course.exercise_uploads.all()})
        return context

    def test_func(self):
        allowed_groups = Group.objects.filter(Q(name='course_coordinators') | Q(name='assistants'))
        usr_groups = self.request.user.groups.all()
        return any(g in allowed_groups for g in usr_groups)

    def post(self, request, *args, **kwargs):
        exercise_pk = self.request.POST['exercise_pk']
        # handle reviews through a separate view
        return ExerciseFeedback.as_view()(request, *args, **kwargs, pk=exercise_pk)


class ExerciseFeedback(UserPassesTestMixin, UpdateView):
    model = Exercise
    form_class = ExerciseFeedbackForm

    def get_success_url(self):
        return HttpResponseRedirect(
            reverse('exercise_uploads_list', kwargs={'slug': self.kwargs['slug']})
        )

    def form_valid(self, form):
        exercise = form.save(commit=False)
        exercise.feedback_by = self.request.user
        exercise.save()
        messages.success(self.request, 'Tilbakemelding vellykket!')
        return self.get_success_url()

    def test_func(self):
        """
        Only course coordinators and assistants can review exercise uploads
        course coordinators can overrule previous reviews, so can the assistants who it themselves.
        """
        if self.get_object().feedback_by is not None:  # there already exists a review
            return self.get_object().feedback_by == self.request.user or \
                   self.request.user.groups.filter(name='course_coordinators').exists()
        return self.request.user.groups.filter(Q(name='assistants') | Q(name='course_coordinators'))


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


class StudentExerciseList(UserPassesTestMixin, TemplateView):
    template_name = 'assignments/exercise_list.html'

    def get_queryset(self):
        return Exercise.objects.filter(course__slug=self.kwargs['slug'])

    def get_context_data(self, **kwargs):
        context = super().get_context_data()
        course = get_object_or_404(Course, slug=self.kwargs['slug'])
        context.update({'course': course,
                        'form': ExerciseFeedbackForm(),
                        'exercise_list': course.exercise_uploads.filter(student=self.request.user)})
        return context

    def test_func(self):
        allowed_groups = Group.objects.filter(name='students')
        usr_groups = self.request.user.groups.all()
        return any(g in allowed_groups for g in usr_groups)
