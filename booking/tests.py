

from django.contrib.auth.models import User
import json
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


class MakeAssistantsAvailableTest(TestCase):

    def setUp(self):
        self.client = Client()
        self.course = Course.objects.create(title='algdat', course_code='tdt4125')
        self.username = 'TEST_USER'
        self.password = 'TEST_PASS'
        self.user = User.objects.create_user(username=self.username, password=self.password)
        self.booking_interval = self.course.booking_intervals.first()
        self.booking_interval.course.assistants.add(self.user)
        self.client.login(username=self.username, password=self.password)

    def test_unauthorized_registration_for_interval(self):
        """An user that is not registered as an assistant in the course should not be able to make
        himself available as an assistant."""

        self.client.logout()
        response = self.client.get(reverse('make_assistants_available'),
                                   {'nk': self.booking_interval.nk})
        self.assertEqual(403, response.status_code, msg="unauthorized users should not be able to access this view")

    def test_authorized_registration_for_interval(self):
        """Assistant registers successfully for an interval"""

        response = self.client.get(reverse('make_assistants_available'),
                                   {'nk': self.booking_interval.nk})
        self.assertEqual(200, response.status_code, msg="authorized users should be able to access this view")

    def test_assistant_registering_for_interval_in_wrong_course(self):
        """
        An assistant that is not an assistant in a specific course should not be able to register for an interval
        """
        # Create course that the assistant is not registered for
        self.course = Course.objects.create(title='matematikk 1', course_code='tdt3423')
        self.booking_interval = self.course.booking_intervals.first()

        response = self.client.get(reverse('make_assistants_available'),
                                   {'nk': self.booking_interval.nk})
        self.assertEqual(403, response.status_code, msg="Only assistants registered for the course should be able to register for intervals")

    def test_make_available_for_interval(self):
        """
        The first assistant registering for an interval
        should result in make_available=False and available_assistants_count=1
        """
        response = self.client.get(reverse('make_assistants_available'),
                                   {'nk': self.booking_interval.nk})
        # Convert the content of type bytes to a dictionary.
        content = response.content
        content = json.loads(content.decode('utf-8'))

        self.assertEqual(200, response.status_code)
        self.assertEqual(content['make_available'], False)
        self.assertEqual(content['available_assistants_count'], 1)

    def test_make_unavailable_for_interval(self):
        """
        An assistant makes himself unavailable for an interval with only one assistant
         should result in make_available=True and available_assistants_count=0
         """
        #Registering the assistant for the interval
        self.booking_interval.assistants.add(self.user)

        response = self.client.get(reverse('make_assistants_available'),
                                   {'nk': self.booking_interval.nk})
        # Convert the content of type bytes to a dictionary.
        content = response.content
        content = json.loads(content.decode('utf-8'))

        self.assertEqual(200, response.status_code)
        self.assertEqual(content['make_available'], True)
        self.assertEqual(content['available_assistants_count'], 0)

