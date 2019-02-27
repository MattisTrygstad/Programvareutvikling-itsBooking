from django.contrib.auth.models import User, Group
from django.db import IntegrityError
from django.test import TestCase, Client
from django.urls import reverse

from .models import Course, BookingInterval


class CourseViewTest(TestCase):

    def setUp(self):
        self.client = Client()
        self.course = Course.objects.create(title='algdat', course_code='tdt4125')

    def test_get_course_detail(self):
        response = self.client.get(reverse('course_detail', kwargs={'slug': self.course.slug}))
        self.assertEqual(200, response.status_code)

    def test_max_assistants_update(self):
        # setup variables
        booking_interval = self.course.booking_intervals.first()
        new_max_num_assistants = 3

        response = self.client.get(reverse('update_max_num_assistants'),
                                   {'nk': booking_interval.nk, 'num': new_max_num_assistants})
        self.assertEqual(403, response.status_code, msg="unauthorized users should not be able to access this view")

        # set the course's course_coordinator and login as them
        cc = User.objects.create_user(username='test', password='123')
        booking_interval.course.course_coordinator = cc
        booking_interval.course.save()
        self.client.login(username='test', password='123')
        response = self.client.get(reverse('update_max_num_assistants'),
                                   {'nk': booking_interval.nk, 'num': new_max_num_assistants})
        self.assertEqual(200, response.status_code)
        # for some reason you need to get the booking_interval object again to detect changes to it
        booking_interval.refresh_from_db()
        self.assertEqual(new_max_num_assistants, booking_interval.max_available_assistants)


class ReservationTest(TestCase):
    def setUp(self):
        self.client = Client()
        self.course = Course.objects.create(title='algdat', course_code='tdt4125')
        self.username = 'STUDENT'
        self.password = '123'
        self.user = User.objects.create_user(username=self.username, password=self.password)
        self.client.login(username=self.username, password=self.password)
        self.student_group = Group.objects.create(name='students')
        self.user.groups.add(self.student_group)

    def test_make_reservation_deny_not_student(self):
        self.student_group.user_set.remove(self.user)
        response = self.client.post(reverse(
            'course_detail', kwargs={'slug': self.course.slug}
            ), {'booking_interval_nk': self.course.booking_intervals.first().nk, 'reservation_index': 0}
        )
        self.assertEqual(403, response.status_code)

    def test_make_reservation_deny_not_available(self):
        response = self.client.post(reverse(
            'course_detail', kwargs={'slug': self.course.slug}
            ), {'reservation_pk': self.course.booking_intervals.first().reservation_intervals.first().pk}
        )
        messages = list(response.context['messages'])
        self.assertEqual(40, messages[0].level)  # level:40 => error

    def test_make_reservation_deny_success(self):
        # setup assistant and booking interval
        assistant_user = User.objects.create_user(username='ASSISTANT', password='123')
        assistant_group = Group.objects.create(name='assistants')
        assistant_group.user_set.add(assistant_user)
        self.course.booking_intervals.first().min_num_assistants = 1
        self.course.booking_intervals.first().assistants.add(assistant_user)
        self.reservation = self.course.booking_intervals.first().reservation_intervals.first()

        response = self.client.post(reverse(
            'course_detail', kwargs={'slug': self.course.slug}
            ), {'reservation_pk': self.reservation.pk}
        )
        messages = list(response.context['messages'])
        self.assertEqual(200, response.status_code)
        self.assertEqual(25, messages[0].level)  # level:25 => success


class CourseModelTest(TestCase):

    def test_create_course(self):
        course = Course.objects.create(title="algdat", course_code="tdt4125")
        self.assertEqual(course.title, "algdat")
        try:
            Course.objects.create(title='algdat', course_code='tdt4125')
        except IntegrityError:
            pass
        else:
            self.fail("duplicate course code values should result in an error")

    def test_course_save(self):
        """Courses are assigned BookingInterval-objects when first saved"""
        course = Course.objects.create(title="algdat", course_code="tdt4125")
        self.assertEqual(Course.objects.filter(title="algdat").count(), 1)
        self.assertEqual(course.booking_intervals.filter(course=course).count(), 25)
        # assert that BookingInterval-objects are assigned only once
        course.save()
        self.assertEqual(course.booking_intervals.filter(course=course).count(), 25)
        # assert that slugs are generated on save()
        self.assertEqual(course.course_code, course.slug)
