from django.contrib.auth.models import User
from django.db import models


#(Tittel, (ingress), innhold, forfatter, timestamp)

class Announcement(models.Model):
    title = models.CharField(max_length=45)
    preamble = models.CharField(max_length=100)
    content = models.TextField(max_length=1500)
    author = models.ForeignKey(User,
                               limit_choices_to={'groups__name': 'course_coordinators'},
                               related_name='announcements' )
    timestamp = models.DateTimeField('date_published')



