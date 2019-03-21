from django.contrib.auth.mixins import UserPassesTestMixin
from django.http import HttpResponseRedirect
from django.shortcuts import get_object_or_404
from django.urls import reverse
from django.utils import timezone
from django.views.generic import CreateView, ListView

from booking.models import Course
from communications.models import Announcement
from itsBooking.templatetags.helpers import user_in_group
from .forms import AnnouncementForm


class AnnouncementListView(UserPassesTestMixin, ListView):
    model = Announcement

    def get_queryset(self):
        course = get_object_or_404(Course, slug=self.kwargs['slug'])
        return Announcement.objects.filter(course=course)

    def get_context_data(self, **kwargs):
        context = super().get_context_data()
        if user_in_group(self.request.user, "course_coordinators"):
            context.update({
                'form': AnnouncementForm()
            })
        return context

    def post(self, request, *args, **kwargs):
        # handle reviews through a separate view
        return CreateAnnouncementView.as_view()(request, *args, **kwargs)

    def test_func(self):
        user = self.request.user
        return user_in_group(user, 'course_coordinators') or user_in_group(user, 'assistants')


class CreateAnnouncementView(CreateView):
    template_name = 'communications/announcement_list.html'
    model = Announcement
    form_class = AnnouncementForm

    def get_success_url(self):
        return HttpResponseRedirect(
            reverse('announcements', kwargs={'slug': self.kwargs['slug']})
        )

    def form_valid(self, form):
        announcement = form.save(commit=False)
        announcement.author = self.request.user
        announcement.course = get_object_or_404(
            Course,
            slug=self.kwargs['slug']
        )
        announcement.save()
        return self.get_success_url()
