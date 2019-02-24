import calendar
import hashlib
from datetime import time

from django.db import models
from django.contrib.auth.models import User, Group
from django.template.defaultfilters import slugify


class Course(models.Model):
    OPEN_BOOKING_TIME = 8
    CLOSE_BOOKING_TIME = 18
    BOOKING_INTERVAL_LENGTH = 2
    RESERVATION_LENGTH = 15
    NUM_DAYS_IN_WORK_WEEK = 5

    title = models.CharField(
        max_length=50,
        unique=True,
    )
    course_code = models.CharField(
        max_length=10,
        unique=True,
    )
    slug = models.SlugField()
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
        for day in range(self.NUM_DAYS_IN_WORK_WEEK):
            for hour in range(self.OPEN_BOOKING_TIME,
                              self.CLOSE_BOOKING_TIME,
                              self.BOOKING_INTERVAL_LENGTH):
                start = time(hour=hour, minute=00)
                end = time(hour=hour + 2, minute=00)
                self.booking_intervals.create(day=day, start=start, end=end)

    def save(self, **kwargs):
        if not self.slug:
            self.slug = slugify(self.course_code)
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


class Reservation(models.Model):
    booking_interval = models.ForeignKey(
        BookingInterval,
        related_name='reservations',
        on_delete=models.CASCADE,
    )
    index = models.IntegerField(
        choices=[(i, i) for i in range(0, 8)],
    )
    student = models.ForeignKey(
        User,
        limit_choices_to={'groups__name': "students"},
        related_name='reservations',
        on_delete=models.CASCADE,
    )
    assistant = models.ForeignKey(
        User,
        limit_choices_to={'groups__name': "assistants"},
        related_name='bookings',
        on_delete=models.CASCADE,
    )

    def _get_available_assistant(self):
        reserved_assistants = User.objects.filter(bookings__index=self.index)
        bi_assistants = self.booking_interval.assistants.all()
        available_assistants = bi_assistants.difference(reserved_assistants)  # all assistants minus reserved ones
        assert available_assistants.count() > 0, 'No assistants available for this reservation interval'
        return available_assistants[0]

    def save(self, **kwargs):
        if self.pk is None:  # if being created, not updated
            self.assistant = self._get_available_assistant()
        super().save(**kwargs)

    def __str__(self):
        return f'{self.booking_interval.course.course_code} - ' \
            f'{time(hour=self.booking_interval.start.hour + self.index//4, minute=(self.index%4)*15).strftime("%H:%M")}-' \
            f'{time(hour=self.booking_interval.start.hour + (self.index+1)// 4, minute=((self.index+1) % 4) * 15).strftime("%H:%M")} - ' \
            f'assistant: {self.assistant} - ' \
            f'student: {self.student}'
