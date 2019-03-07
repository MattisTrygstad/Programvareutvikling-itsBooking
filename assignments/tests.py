import tempfile

from django.contrib.auth.models import User
from django.test import TestCase
from django.urls import reverse, reverse_lazy

from assignments.models import Exercise
from booking.models import Course


class ReservationTest(TestCase):

    def setUp(self):
        self.course = Course.objects.create(title='algdat', course_code='tdt4125')
        self.username = 'STUDENT'
        self.password = '123'
        self.user = User.objects.create_user(username=self.username, password=self.password)
        self.client.login(username=self.username, password=self.password)

    def test_file_upload(self):
        prev_count = Exercise.objects.count()
        with open('manage.py') as f:
            response = self.client.post(
                reverse('upload_exercise', kwargs={'slug': self.course.slug}),
                {'file': f}
            )
            self.assertEqual(302, response.status_code)
            self.assertEqual(prev_count + 1, Exercise.objects.count())

    def test_post_upload_no_file_fail(self):
        prev_count = Exercise.objects.count()
        response = self.client.post(
            reverse('upload_exercise', kwargs={'slug': self.course.slug})
        )
        self.assertFormError(response, 'form', 'file', 'Feltet er påkrevet.')

    def test_get_upload_page(self):
        response = self.client.get(reverse('upload_exercise', kwargs={'slug': self.course.slug}))
        self.assertEqual(200, response.status_code)

    def test_get_uploads_list(self):
        response = self.client.get(reverse_lazy('exercise_uploads_list'))
        self.assertEqual(200, response.status_code)
