import datetime
from django.contrib.auth.models import User
from django.db import models
import datetime
from django.utils import timezone


class Announcement(models.Model):
    title = models.CharField(max_length=45)
    preamble = models.CharField(max_length=100)
    content = models.TextField(max_length=1500)
    author = models.ForeignKey(User,
                               limit_choices_to={'groups__name': 'course_coordinators'},
                               related_name='announcements' )
    timestamp = models.DateTimeField('date_published')

    def __str__(self):
        return self.title


