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
            
            objects = BookingInterval.objects.filter(Q(start=time(hour=hour)) & Q(course=self.object))
            interval = {
                'start': time(hour),
                'stop': time(hour + Course.BOOKING_INTERVAL_LENGTH),
                'objects': objects,
                'assistants': objects[0].assistants.values_list('id')
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

def make_assistants_available(request):
    nk = request.GET.get('nk', None)
    booking_interval = BookingInterval.objects.get(nk=nk)


    if not booking_interval.course.assistants.filter(id=request.user.id).exists():
        raise PermissionDenied()
    if not booking_interval.assistants.filter(id=request.user.id).exists():
        booking_interval.assistants.add(request.user.id)
        make_available=False
    else:
        booking_interval.assistants.remove(request.user.id)
        make_available = True
    available_assistants_count=booking_interval.assistants.all().count()
    data = {
        'make_available': make_available,
        'available_assistants_count': available_assistants_count,
    }
    return JsonResponse(data)


