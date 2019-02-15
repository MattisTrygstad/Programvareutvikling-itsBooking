import calendar
import hashlib
import datetime

from django.db import models
from django.contrib.auth.models import User, Group
#from booking.helpers import generate_booking_intervals


class Course(models.Model):
    title = models.CharField(
        max_length=50,
        unique=True,
    )
    course_code = models.CharField(
        max_length=10,
        unique=True,
    )
    students = models.ManyToManyField(
        User,
        limit_choices_to={'groups__name': "students"},
        related_name="enrolled_courses",
        blank=True,
    )
    assistants = models.ManyToManyField(
        User,
        limit_choices_to={'groups__name': "assistants"},
        related_name="assisting_courses",
        blank=True,
    )
    course_coordinator = models.OneToOneField(
        User,
        limit_choices_to={'groups__name': "course_coordinators"},
        blank=True,
        null=True,
        on_delete=models.CASCADE,
        related_name="course",
    )

    def __str__(self):
        return self.title

    def _generate_booking_intervals(self):
        '''Generate five booking intervals for a course'''
        for i in range(5):
            day = calendar.day_name[i]
            for interval in range(5):
                hour = 8
                start = datetime.time(hour=hour, minute=00)
                end = datetime.time(hour=hour + 2, minute=00)
                self.booking_interval.create(day=day, start=start, end=end)
                hour += 2

    def save(self,**kwargs):
        super().save(**kwargs)
        self._generate_booking_intervals()



class BookingInterval(models.Model):
    DAY_CHOICES = [(str(i), list(calendar.day_name)[i]) for i in range(0, 5)]

    course = models.ForeignKey(
        Course,
        related_name='booking_interval',
        on_delete=models.CASCADE,
    )
    day = models.CharField(
        max_length=20,
        choices=DAY_CHOICES,
    )
    start = models.TimeField()
    end = models.TimeField()
    min_available_assistants = models.IntegerField(
        default=0,
        blank=True,
        null=True,  # None => interval closed for assistants and booking
    )
    assistants = models.ManyToManyField(
        User,
        limit_choices_to={'groups__name': "assistants"},
        blank=True,
        related_name='setup_assistant_hours',
    )
    nk = models.CharField(
        max_length=32,
        blank=False,
        unique=True,
        primary_key=True,
    )

    def save(self, **kwargs):
        if not self.nk:
            secure_hash = hashlib.md5()
            secure_hash.update(
                f'{self.start}:{self.get_day_display()}:{self.course}'.encode(
                    'utf-8'))
            self.nk = secure_hash.hexdigest()
        super().save(**kwargs)


    def __str__(self):
        return self.course + " "  + self.day + " " + self.start + " " + self.end


