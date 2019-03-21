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

    def test_no_announcement_list(self):
        """
        If no announcement_list exists, an appropriate message is displayed
        """
        response = self.client.get(reverse('announcements', kwargs={'slug': self.course.slug}))
        self.assertEqual(response.status_code, 200)
        # self.assertContains(response, "Ingen kunngjøringer tilgjengelig")
        self.assertQuerysetEqual(response.context['announcement_list'], [],
                                 msg="There should not be announcement_list in context")

    def test_one_announcement(self):
        """
        The announcement_list page should display the announcement
        """
        Announcement.objects.create(
            title="Test announcement1",
            content="heiehie",
            author=self.user,
            course=self.course)
        response = self.client.get(reverse('announcements', kwargs={'slug': self.course.slug}))
        self.assertQuerysetEqual(
            response.context['announcement_list'].order_by('title'),
            ['<Announcement: Test announcement1>']
        )

    def test_two_announcement_list(self):
        """
        The announcement_list page may display multiple announcement_list.
        """
        Announcement.objects.create(title="Test announcement1", content="heiehie", author=self.user, course=self.course)
        Announcement.objects.create(title="Test announcement2", content="heiehie", author=self.user, course=self.course)
        response = self.client.get(reverse('announcements', kwargs={'slug': self.course.slug}))
        self.assertQuerysetEqual(
            response.context['announcement_list'].order_by('title'),
            ['<Announcement: Test announcement1>', '<Announcement: Test announcement2>']
        )

    def test_announcements_list_page_testfunc(self):
        # logged in as cc
        response = self.client.get(reverse('announcements', kwargs={'slug': self.course.slug}))
        self.assertEqual(200, response.status_code)
        self.assertIsNotNone(response.context['form'], "AnnouncementForm must be included for ccs")

        # forbidden for users who are not cc or assistant
        Group.objects.get(name="course_coordinators").user_set.remove(self.user)
        response = self.client.get(reverse('announcements', kwargs={'slug': self.course.slug}))
        self.assertEqual(403, response.status_code)

        # assistants have access to the page, but not the form
        self.user.groups.add(Group.objects.create(name="assistants"))
        response = self.client.get(reverse('announcements', kwargs={'slug': self.course.slug}))
        self.assertEqual(200, response.status_code)
        with self.assertRaises(KeyError):
            response.context['form']  # keyError proves the form is not included in the response

    def test_create_announcement_deny_not_course_coordinator(self):
        """
        It should not be possible to create an announcement if you are not a course coordinator
        """
        self.cc_group.user_set.remove(self.user)
        response = self.client.post(reverse(
            'announcements', kwargs={'slug': self.course.slug}
        ), {'title': 'Test Announcement', 'content': 'Test content'}
        )
        self.assertEqual(Announcement.objects.all().__str__(), '<QuerySet []>')
        self.assertEqual(403, response.status_code)

    def test_create_announcement_success(self):
        """
        It should be possible to create an announcemnt if you are a course coordinator
        """
        response = self.client.post(reverse(
            'announcements', kwargs={'slug': self.course.slug}
        ), {'title': 'Test Announcement', 'content': 'Test content'}
        )
        self.assertEqual(302, response.status_code)
        self.assertEqual(Announcement.objects.all().__str__(), '<QuerySet [<Announcement: Test Announcement>]>', )
