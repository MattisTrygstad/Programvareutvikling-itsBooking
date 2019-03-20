from django.contrib.auth.models import User
from django.db import models
from booking.models import Course


def get_avatar_image_path(instance, filename):
    return f'avatars/user_{instance.student.id}/{filename}/'


class Announcement(models.Model):
    title = models.CharField(
        max_length=45
    )
    content = models.TextField(
        max_length=1500
    )
    author = models.ForeignKey(
        User,
        limit_choices_to={'groups__name': 'course_coordinators'},
        related_name='announcements',
        on_delete=models.CASCADE,
    )
    course = models.ForeignKey(
        Course,
        related_name='announcement',
        on_delete=models.CASCADE,
    )
    timestamp = models.DateTimeField(
        auto_now_add=True
    )

    def __str__(self):
        return self.title


class Avatar(models.Model):
    user = models.OneToOneField(
        User,
        on_delete=models.CASCADE,
    )
    image = models.ImageField(
        upload_to=get_avatar_image_path,
    )
