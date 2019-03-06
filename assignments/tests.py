import tempfile

from django.contrib.auth.models import User, Group
from django.test import TestCase, Client
from django.urls import reverse, reverse_lazy

from booking.models import Course


class ReservationTest(TestCase):

    def setUp(self):
        self.course = Course.objects.create(title='algdat', course_code='tdt4125')
        self.username = 'STUDENT'
        self.password = '123'
        self.user = User.objects.create_user(username=self.username, password=self.password)
        self.client.login(username=self.username, password=self.password)

    def test_file_upload(self):
        response = self.client.post(
            reverse('upload_exercise', kwargs={'slug': self.course.slug}),
            {'file': list(tempfile.TemporaryFile())}
        )
        self.assertEqual(200, response.status_code)

    def test_get_upload_page(self):
        response = self.client.get(reverse('upload_exercise', kwargs={'slug': self.course.slug}))
        self.assertEqual(200, response.status_code)

    def test_get_uploads_list(self):
        response = self.client.get(reverse_lazy('exercise_uploads_list'))
        self.assertEqual(200, response.status_code)
