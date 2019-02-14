from django.contrib.auth.models import User
from django.test import TestCase, Client
from django.urls import reverse_lazy

from django.conf import settings


class TestBaseViews(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(username='username', password='123')
        self.user.save()
        self.client = Client()
        self.client.login(username='username', password='123')

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

    def test_login_fail(self):
        self.client.logout()
        # wrong username
        response = self.client.post(reverse_lazy('login'), {'username': 'WRONG', 'password': '123'})
        self.assertNotEqual(302, response.status_code)
        # wrong password
        response = self.client.post(reverse_lazy('login'), {'username': 'username', 'password': 'WRONG'})
        self.assertNotEqual(302, response.status_code)

    def test_login_success(self):
        self.client.logout()
        response = self.client.post(reverse_lazy('login'), {'username': 'username', 'password': '123'})
        self.assertEqual(302, response.status_code)

    def test_logout_fail(self):
        # handle logout request from anonymousUser
        self.client.logout()
        response = self.client.post(reverse_lazy('logout'))
        self.assertNotEqual(500, response.status_code)

    def test_logout_success(self):
        # test both get and post
        response = self.client.post(reverse_lazy('logout'))
        self.assertEqual(302, response.status_code)
        response = self.client.get(reverse_lazy('logout'))
        self.assertEqual(302, response.status_code)



