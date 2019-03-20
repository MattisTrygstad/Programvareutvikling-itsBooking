from django.contrib.auth.models import User, Group
from django.urls import reverse
from booking.models import Course
from communications.models import Announcement
from django.test import TestCase, Client
from django.utils import timezone


class AnnouncementModelTests(TestCase):
    def testCreateAnnouncement(self):
        """
        Create announcement and check that timestamp is correct
        """
        before_time = timezone.now()
        announcement = Announcement(title="Test announcement", content="heiehie")
        after_time = timezone.now()
        self.assertIs(announcement.timestamp >= before_time, True, msg="Timestamp is not correct")
        self.assertIs(announcement.timestamp <= after_time, True, msg="Timestamp is not correct")


class AnnouncementViewTest(TestCase):
    def setUp(self):
        """
        Runs before every test
        """
        self.client = Client()
        self.course = Course.objects.create(title='algdat', course_code='tdt4125')
        self.username = 'CC'
        self.password = '123'
        self.user = User.objects.create_user(username=self.username, password=self.password)
        self.client.login(username=self.username, password=self.password)
        self.cc_group = Group.objects.create(name='course_coordinators')
        self.user.groups.add(self.cc_group)

    def test_no_announcements(self):
        """
        If no announcements exists, an appropriate message is displayed
        """
        response = self.client.get(reverse('announcements', kwargs={'slug': self.course.slug}))
        self.assertEqual(response.status_code, 200)
        # self.assertContains(response, "Ingen kunngjøringer tilgjengelig")
        self.assertQuerysetEqual(response.context['announcements'], [],
                                 msg="There should not be announcements in context")

    def test_one_annoucement(self):
        """
        The announcements page should display the announcement
        """
        Announcement.objects.create(title="Test announcement1", content="heiehie", author=self.user, course=self.course)
        response = self.client.get(reverse('announcements', kwargs={'slug': self.course.slug}))
        self.assertQuerysetEqual(
            response.context['announcements'].order_by('title'),
            ['<Announcement: Test announcement1>']
        )

    def test_two_announcements(self):
        """
        The announcements page may display multiple announcements.
        """
        Announcement.objects.create(title="Test announcement1", content="heiehie", author=self.user, course=self.course)
        Announcement.objects.create(title="Test announcement2", content="heiehie", author=self.user, course=self.course)
        response = self.client.get(reverse('announcements', kwargs={'slug': self.course.slug}))
        self.assertQuerysetEqual(
            response.context['announcements'].order_by('title'),
            ['<Announcement: Test announcement1>', '<Announcement: Test announcement2>']
        )