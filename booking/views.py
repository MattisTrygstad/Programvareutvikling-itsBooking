import calendar
from datetime import time

from django.contrib import messages
from django.contrib.auth.mixins import UserPassesTestMixin
from django.core.exceptions import PermissionDenied
from django.db.models import Q
from django.http import HttpResponse, JsonResponse, HttpResponseRedirect
from django.urls import reverse
from django.views.generic import DetailView, ListView, FormView
from django.views.generic.base import View, TemplateView

from booking.forms import ReservationConnectionForm
from booking.models import Course, BookingInterval, ReservationInterval, ReservationConnection
from itsBooking.templatetags.helpers import name
from itsBooking.views import LoginView

WEEKDAYS = list(calendar.day_name)[0:5]


class TableView(DetailView):
    model = Course
    template_name = 'booking/course_detail.html'


class StudentTable(TableView):
    model = Course
    template_name = 'booking/course_detail.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['weekdays'] = WEEKDAYS
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
                    'reservations': [r.reservation_intervals.filter(index=i).first() for r in
                                     booking_intervals.prefetch_related('reservation_intervals')],
                }
                    for i in range(Course.NUM_RESERVATIONS_IN_BOOKING_INTERVAL)
                ]
            }
            intervals.append(interval)
        context['intervals'] = intervals
        context['form'] = ReservationConnectionForm()
        return context

    def post(self, request, *args, **kwargs):
        return CreateReservationConnection.as_view()(request, *args, **kwargs)


class AssistantTable(TableView):

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['weekdays'] = WEEKDAYS
        intervals = []
        for hour in range(Course.OPEN_BOOKING_TIME, Course.CLOSE_BOOKING_TIME, Course.BOOKING_INTERVAL_LENGTH):
            booking_intervals = BookingInterval.objects.filter(Q(start=time(hour=hour)) & Q(course=self.object))
            interval = {
                'start': time(hour),
                'stop': time(hour + Course.BOOKING_INTERVAL_LENGTH),
                'booking_intervals': booking_intervals,
            }
            intervals.append(interval)
        context['intervals'] = intervals
        return context


class CourseCoordinatorTable(StudentTable):

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        booking_intervals = BookingInterval.objects.filter(course=self.object)
        assistants_registered_for_bi = []
        booked_counter, available_intervals, full_booking_intervals = 0, 0, 0
        for booking_interval in booking_intervals:
            # Assistants registered for a booking interval
            for assistant in booking_interval.assistants.all():
                assistants_registered_for_bi.append(assistant)
            # Share of reservation_intervals booked by students
            for reservation_interval in booking_interval.reservation_intervals.all():
                available_intervals += booking_interval.assistants.count()
                booked_counter += reservation_interval.connections.count()
            # Number of full booking intervals
            if booking_interval.max_available_assistants == booking_interval.assistants.count():
                full_booking_intervals += 1
        context['assistants_registered_for_bi'] = list(set(assistants_registered_for_bi))
        context['booked_ri_count'] = booked_counter
        context['available_rintervals_count'] = available_intervals  # Reservation intervals available for students
        context['full_bi_count'] = full_booking_intervals
        context['available_bintervals_count'] = booking_intervals.all().count()  # Number of available booking intervals
        context['available_assistants'] = Course.objects.get(pk=self.object.pk).assistants.all().count()
        context['total_opening_time'] = booking_intervals.filter(max_available_assistants__gt=0).all().count() * 2

        # Percentages for progress bar at cc_overview
        context['assistant_percent'] = round(len(context['assistants_registered_for_bi']) / context['available_assistants'] * 100) \
            if context['available_assistants'] != 0 else 0
        context['student_percent'] = round(context['booked_ri_count'] / context['available_rintervals_count'] * 100) \
            if context['available_rintervals_count'] != 0 else 0
        context['max_studass_percent'] = round(context['full_bi_count'] / context['available_bintervals_count'] * 100) \
            if context['available_bintervals_count'] != 0 else 0

        return context


class CreateReservationConnection(UserPassesTestMixin, FormView):
    form_class = ReservationConnectionForm
    template_name = 'booking/reservation_input.html'

    def get_success_url(self):
        return reverse('course_detail', kwargs={'slug': self.kwargs['slug']})

    def test_func(self):
        return self.request.user.groups.filter(name='students').exists()

    def form_valid(self, form):
        reservation_interval = ReservationInterval.objects.get(pk=form.cleaned_data['reservation_pk'])
        reservation_connection = ReservationConnection.objects.create(
            reservation_interval=reservation_interval, student=self.request.user
        )
        success_message = f'Reservasjon opprettet! Din stud. ass. er {name(reservation_connection.assistant)}'
        messages.success(self.request, success_message)
        return super().form_valid(form)

    def form_invalid(self, form):
        error_message = 'Det oppsto en feil under opprettelsen av din reservajon. Vennligst prøv igjen.'
        messages.error(self.request, error_message)
        return super().form_invalid(form)


class CourseDetailDelegator(View):
    delegator = {
        'students': StudentTable.as_view(),
        'assistants': AssistantTable.as_view(),
        'course_coordinators': CourseCoordinatorTable.as_view(),
    }

    def dispatch(self, request, *args, **kwargs):
        # if user not logged in or not in any groups -> 403, if user is missing groups -> Login page
        if not request.user.is_authenticated or not request.user.groups.all():
            raise PermissionDenied
        request_user_group = self.request.user.groups.first().name
        return self.delegator.get(request_user_group, LoginView.as_view())(request, *args, **kwargs)


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
        registration_available = False
    else:
        booking_interval.assistants.remove(request.user.id)
        registration_available = True
    available_assistants_count = booking_interval.assistants.all().count()
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
        context = super().get_context_data()
        context.update({'days': WEEKDAYS})
        return context

    def test_func(self):
        return self.request.user.groups.filter(name="students").exists()

    def post(self, request):
        try:
            rc = ReservationConnection.objects.get(pk=request.POST['reservation_connection_pk'])
            if rc.student == self.request.user:
                rc.delete()
                success_message = f'Du er nå meldt av reservasjonen!'
                messages.success(request, success_message)
                return HttpResponseRedirect(request.path)
            else:
                raise PermissionDenied("Fy!")
        except ReservationConnection.DoesNotExist:
            error_message = 'Det oppsto en feil ved avmelding av din reservajon. Vennligst prøv igjen.'
            messages.error(request, error_message)
            return self.get(request)


class AssistantReservationList(UserPassesTestMixin, TemplateView):
    template_name = 'booking/assistant_reservation_list.html'

    def get_context_data(self, *, object_list=None, **kwargs):
        context = super().get_context_data()
        bis = BookingInterval.objects.filter(assistants=self.request.user)
        booking_intervals = []
        for booking_interval in bis:
            reservation_intervals = booking_interval.reservation_intervals.all()
            booking_intervals.append(
                {
                    'booking_interval': booking_interval,
                    'reservation_intervals': [
                        {
                            'reservation_interval': reservation_interval,
                            'connection': reservation_interval.connections.filter(assistant=self.request.user).first(),
                        }
                        for reservation_interval in reservation_intervals],

                }
            )
        context.update({
            'booking_intervals': booking_intervals
        })
        return context

    def test_func(self):
        return self.request.user.groups.filter(name="assistants").exists()

