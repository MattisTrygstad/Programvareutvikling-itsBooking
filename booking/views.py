import calendar
from datetime import time

from django.contrib import messages
from django.contrib.auth.mixins import UserPassesTestMixin
from django.core.exceptions import PermissionDenied
from django.db.models import Q
from django.http import HttpResponse, JsonResponse, HttpResponseForbidden, HttpResponseRedirect
from django.views.generic import DetailView, ListView
from django.shortcuts import render

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
                'assistants': booking_intervals.first().assistants.values_list('id'),
                'reservation_intervals': [{
                    'start': time(hour=hour + (15 * i) // 60, minute=(15 * i) % 60),
                    'stop': time(hour=hour + (15 * (i + 1)) // 60, minute=(15 * (i + 1)) % 60),
                    'reservations': sorted(list(ReservationInterval.objects.filter(
                            Q(index=i) & Q(booking_interval__in=booking_intervals)
                        )), key=lambda r: r.booking_interval.day),
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

def bi_registration_switch(request):
    nk = request.GET.get('nk', None)
    booking_interval = BookingInterval.objects.get(nk=nk)


    if not booking_interval.course.assistants.filter(id=request.user.id).exists():
        raise PermissionDenied()
    if not booking_interval.assistants.filter(id=request.user.id).exists():
        booking_interval.assistants.add(request.user.id)
        registration_available=False
    else:
        booking_interval.assistants.remove(request.user.id)
        registration_available = True
    available_assistants_count=booking_interval.assistants.all().count()
    data = {
        'registration_available': registration_available,
        'available_assistants_count': available_assistants_count,
    }
    return JsonResponse(data)



class ReservationList(UserPassesTestMixin, ListView):
    template_name = 'booking/reservation_list.html'

    def get_queryset(self):
        return ReservationConnection.objects.filter(student=self.request.user)

    def get_context_data(self, *, object_list=None, **kwargs):
        self.object_list = self.get_queryset()
        context = super().get_context_data(object_list=object_list, **kwargs)
        context.update({'days' : list(calendar.day_name)[0:5]})
        return context

    def test_func(self):
        return self.request.user.groups.filter(name="students").exists()

    def post(self, request):
        try:
            rc = ReservationConnection.objects.get(pk=request.POST['id_rc_pk'])
            if rc.student == self.request.user:
                rc.delete()
                messagetext = f'Du er nå meldt av reservasjonen!'
                messages.success(request,messagetext)
                return HttpResponseRedirect(request.path)
            else:
                return PermissionDenied("Fy!")
        except ReservationConnection.DoesNotExist:
            # user message.error instead of form.errors, they force hidden form fields to be shown
            messages.error(request, 'Det oppsto en feil ved avmelding av din reservajon. Vennligst prøv igjen.')
            return self.get(request)

