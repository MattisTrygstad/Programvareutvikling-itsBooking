from django.contrib import auth
from django.contrib.auth.models import User
from django.db import IntegrityError
from django.test import TestCase, Client
from django.urls import reverse

from .models import Course


class CourseViewTest(TestCase):

    def setUp(self):
        self.client = Client()
        self.course = Course.objects.create(title='algdat', course_code='tdt4125')

    def test_get_course_detail(self):
        response = self.client.get(reverse('course_detail', kwargs={'slug': self.course.slug}))
        self.assertEqual(200, response.status_code)

    def test_min_assistants_update(self):
        # setup variables
        booking_interval = self.course.booking_intervals.first()
        new_min_num_assistants = 3

        response = self.client.get(reverse('update_min_num_assistants'),
                                   {'nk': booking_interval.nk, 'num': new_min_num_assistants})
        self.assertEqual(403, response.status_code, msg="unauthorized users should not be able to access this view")

        # set the course's course_coordinator and login as them
        cc = User.objects.create_user(username='test', password='123')
        booking_interval.course.course_coordinator = cc
        booking_interval.course.save()
        self.client.login(username='test', password='123')

        response = self.client.get(reverse('update_min_num_assistants'),
                                   {'nk': booking_interval.nk, 'num': new_min_num_assistants})
        self.assertEqual(200, response.status_code)
        # for some reason you need to get the booking_interval object again to detect changes to it
        self.assertEqual(new_min_num_assistants, self.course.booking_intervals.first().min_available_assistants)


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
