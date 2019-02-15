import calendar

from django.views.generic import DetailView

from booking.models import Course


class CourseDetail(DetailView):
    model = Course

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['weekdays'] = list(calendar.day_name)[0:5]
        return context

