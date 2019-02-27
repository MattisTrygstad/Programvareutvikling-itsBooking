import calendar
from datetime import time

from django.contrib import messages
from django.core.exceptions import PermissionDenied
from django.db.models import Q
from django.http import HttpResponse
from django.views.generic import DetailView

from booking.forms import ReservationForm
from booking.models import Course, BookingInterval, ReservationInterval, ReservationConnection
from itsBooking.templatetags.helpers import name


class CreateReservationView(DetailView):
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
                'booking_intervals': booking_intervals,
                'reservation_intervals': [{
                    'start': time(hour=hour + (15 * i) // 60, minute=(15 * i) % 60),
                    'stop': time(hour=hour + (15 * (i + 1)) // 60, minute=(15 * (i + 1)) % 60),
                    'reservations': ReservationInterval.objects.filter(
                            Q(index=i) & Q(booking_interval__in=booking_intervals)
                        ),
                    }
                    for i in range(Course.NUM_RESERVATIONS_IN_BOOKING_INTERVAL)
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
                reservation_interval = ReservationInterval.objects.get(pk=form.cleaned_data['reservation_pk'])
                reservation_connection = ReservationConnection.objects.create(
                    reservation_interval=reservation_interval, student=request.user
                )

                # add success message
                success_message = self.get_success_message(reservation_connection)
                if success_message:
                    messages.success(request, success_message)

                self.object = self.get_object()
                return self.render_to_response(context=self.get_context_data())
            else:
                # user message.error instead of form.errors, they force hidden form fields to be shown
                messages.error(request, 'Det oppsto en feil under opprettelsen av din reservajon. Vennligst prøv igjen.')
                return self.get(request, *args, **kwargs)
        else:
            raise PermissionDenied()

    def get_success_message(self, reservation_connection):
        return f'Reservasjon opprettet! Din stud. ass. er {name(reservation_connection.assistant)}'


def update_max_num_assistants(request):
    nk = request.GET.get('nk', None)
    num = request.GET.get('num', None)
    booking_interval = BookingInterval.objects.get(nk=nk)

    if request.user == booking_interval.course.course_coordinator:
        booking_interval.max_available_assistants = num
        booking_interval.save()
        return HttpResponse('')

    raise PermissionDenied()

