import calendar
from datetime import time

from django.contrib import messages
from django.core.exceptions import PermissionDenied
from django.db.models import Q
from django.http import HttpResponse
from django.views.generic import DetailView

from booking.forms import ReservationForm
from booking.models import Course, BookingInterval
from itsBooking.templatetags.helpers import name


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
                'interval_reservation_intervals': [
                    {
                        'start': time(hour=hour + (15*i)//60, minute=(15*i) % 60),
                        'stop': time(hour=hour + (15*(i+1))//60, minute=(15*(i+1)) % 60),
                        'index': i,
                        'reservations': [
                            {
                             'free_slots': bi.assistants.count() - bi.reservations.filter(index=i).count(),
                             'num_assistants': bi.assistants.count(),
                             'min_available_assistants': bi.min_available_assistants,
                             'parent_booking_interval': bi
                            }
                            for bi in booking_intervals
                        ],
                    }
                    for i in range(0, 8)
                ]
            }
            intervals.append(interval)
        context['intervals'] = intervals
        context['form'] = ReservationForm()
        return context

    def post(self, request, *args, **kwargs):
        form = ReservationForm(request.POST, request.FILES)
        if request.user.groups.filter(name='students').exists():
            if form.is_valid():
                # create reservation
                bi = BookingInterval.objects.get(nk=form.cleaned_data['booking_interval_nk'])
                index = form.cleaned_data['reservation_index']
                reservation = Reservation.objects.create(booking_interval=bi, index=index, student=request.user)

                # add success message
                success_message = self.get_success_message(reservation)
                if success_message:
                    messages.success(request, success_message)

                self.object = self.get_object()
                return self.render_to_response(context=self.get_context_data())
            else:
                # dont use form.errors, they force hidden form fields to be shown
                messages.error(request, 'Det oppsto en feil under opprettelsen av din reservajon. Vennligst prøv igjen.')
                return self.get(request, *args, **kwargs)
        else:
            raise PermissionDenied()

    def get_success_message(self, reservation):
        return f'Reservasjon opprettet! Din stud. ass. er {name(reservation.assistant)}'


def update_min_num_assistants(request):
    nk = request.GET.get('nk', None)
    num = request.GET.get('num', None)
    booking_interval = BookingInterval.objects.get(nk=nk)

    if request.user == booking_interval.course.course_coordinator:
        booking_interval.min_available_assistants = num if num != '' else None
        booking_interval.save()
        return HttpResponse('')

    raise PermissionDenied()

