from django.http import HttpResponseRedirect
from django.urls import reverse
from django.utils import timezone
from django.views.generic import CreateView, TemplateView
from communications.models import Announcement
from .forms import AnnouncementForm


class AnnouncementView(TemplateView):
    template_name = 'communications/announcements.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data()
        announcements = Announcement.objects.all()
        context.update({'announcements': announcements,
                        'form': AnnouncementForm()})
        return context

    def post(self, request, *args, **kwargs):
        # handle reviews through a separate view
        return CreateAnnouncementView.as_view()(request, *args, **kwargs)

class CreateAnnouncementView(CreateView):
    template_name = 'communications/announcements.html'
    model = Announcement
    form_class = AnnouncementForm

    def get_success_url(self):
        return HttpResponseRedirect(
            reverse('announcements', kwargs={'slug': self.kwargs['slug']})
        )

    def form_valid(self, form):
        announcement = form.save(commit=False)
        announcement.author = self.request.user
        announcement.timestamp = timezone.now()
        announcement.save()
        return self.get_success_url()
