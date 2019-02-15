import calendar
from datetime import time

from django.db.models import Q
from django.views.generic import DetailView

from booking.models import Course, BookingInterval


class CourseDetail(DetailView):
    model = Course

    def get_interval_objects(self, start_time):
        return BookingInterval.objects.filter(
            Q(start=time(hour=int(start_time))) & Q(course=self.object)
        )

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['weekdays'] = list(calendar.day_name)[0:5]
        intervals = []
        for hour in range(Course.OPEN_BOOKING_TIME, Course.CLOSE_BOOKING_TIME, Course.BOOKING_INTERVAL_LENGTH):
            interval = {
                'start': time(hour),
                'stop': time(hour + Course.BOOKING_INTERVAL_LENGTH),
                'objects': BookingInterval.objects.filter(Q(start=time(hour=hour)) & Q(course=self.object))
            }
            intervals.append(interval)
        context['intervals'] = intervals
        return context

