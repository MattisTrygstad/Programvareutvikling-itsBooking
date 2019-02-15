import calendar
import hashlib
import datetime

from django.db import models
from django.contrib.auth.models import User, Group


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
        """
        generates booking intervals associated with a course. 5 2-hour intervals for every weekday
        """
        for day in range(5):
            for hour in range(8, 18, 2):
                start = datetime.time(hour=hour, minute=00)
                end = datetime.time(hour=hour + 2, minute=00)
                BookingInterval.objects.create(day=day, start=start, end=end, course=self)

    def save(self, **kwargs):
        super().save(**kwargs)
        if not self.booking_intervals.all():
            self._generate_booking_intervals()
        super().save()


class BookingInterval(models.Model):
    DAY_CHOICES = [(str(i), calendar.day_name[i]) for i in range(0, 5)]

    course = models.ForeignKey(
        Course,
        related_name='booking_intervals',
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

    class Meta:
        ordering = [
            '-course', 'day', 'start'
        ]

    def save(self, **kwargs):
        if not self.nk:
            secure_hash = hashlib.md5()
            secure_hash.update(
                f'{self.start}-{self.get_day_display()}-{self.course}'.encode(
                    'utf-8'))
            self.nk = secure_hash.hexdigest()
        super().save(**kwargs)

    def __str__(self):
        return f'{self.course.course_code} {self.get_day_display()} {self.start}-{self.end}'


