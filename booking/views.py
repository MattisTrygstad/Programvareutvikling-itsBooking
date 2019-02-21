import calendar
from datetime import time

from django.core.exceptions import PermissionDenied
from django.db.models import Q
from django.http import HttpResponse
from django.views.generic import DetailView

from booking.models import Course, BookingInterval


class BookingView(DetailView):
    model = Course
    template_name = 'booking/course_detail.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['weekdays'] = list(calendar.day_name)[0:5]
        intervals = []
        for hour in range(Course.OPEN_BOOKING_TIME, Course.CLOSE_BOOKING_TIME, Course.BOOKING_INTERVAL_LENGTH):
            booking_intervals = BookingInterval.objects.filter(Q(start=time(hour=hour)) & Q(course=self.object))
            interval = {
                'start': time(hour),
                'stop': time(hour + Course.BOOKING_INTERVAL_LENGTH),
                'objects': booking_intervals,
                'reservations_intervals': [
                    {
                        'start': time(hour=hour + (15*i)//60, minute=(15*i) % 60),
                        'stop': time(hour=hour + (15*(i+1))//60, minute=(15*(i+1)) % 60),
                        'index': i,
                        'reservations': [
                            (bi.assistants.count() - bi.reservations.filter(index=i).count(),
                             bi.assistants.count(), bi.min_available_assistants)
                            for bi in booking_intervals
                        ],
                    }
                    for i in range(0, 8)
                ]
            }
            intervals.append(interval)
        context['intervals'] = intervals
        return context


def update_min_num_assistants(request):
    nk = request.GET.get('nk', None)
    num = request.GET.get('num', None)
    booking_interval = BookingInterval.objects.get(nk=nk)

    if request.user == booking_interval.course.course_coordinator:
        booking_interval.min_available_assistants = num if num != '' else None
        booking_interval.save()
        return HttpResponse('')

    raise PermissionDenied()

