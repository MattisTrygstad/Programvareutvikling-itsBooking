from django.test import TestCase, Client
from django.urls import reverse_lazy

from django.conf import settings


class TestBaseViews(TestCase):
    def setUp(self):
        self.client = Client()

    def test_populate(self):
        # populate should redirect to home when DEBUG=True and deny permission otherwise
        settings.DEBUG = True
        response = self.client.get(reverse_lazy('populate'))
        self.assertEqual(302, response.status_code)
        settings.DEBUG = False
        response = self.client.get(reverse_lazy('populate'))
        self.assertEqual(403, response.status_code)

    def test_home(self):
        response = self.client.get(reverse_lazy('home'))
        self.assertEqual(200, response.status_code)
