import calendar
from datetime import time

from django.core.exceptions import PermissionDenied
from django.db.models import Q
from django.http import HttpResponse, JsonResponse
from django.views.generic import DetailView

from booking.models import Course, BookingInterval


class CourseDetail(DetailView):
    model = Course

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


def update_min_num_assistants(request):
    nk = request.GET.get('nk', None)
    num = request.GET.get('num', None)
    booking_interval = BookingInterval.objects.get(nk=nk)

    if request.user == booking_interval.course.course_coordinator:
        booking_interval.min_available_assistants = num
        booking_interval.save()
        return HttpResponse('')

    raise PermissionDenied()

def make_assistants_available(request):
    make_available=False
    nk = request.GET.get('nk', None)
    booking_interval = BookingInterval.objects.get(nk=nk)
    print("Hei")
    if not booking_interval.assistants.filter(id=request.user.id).exists():
        booking_interval.assistants.add(request.user.id)
        make_available=False
        print(booking_interval.assistants.all())
    else:
        booking_interval.assistants.remove(request.user.id)
        make_available = True
    data = {
        'make_available': make_available,
    }
    return JsonResponse(data)


