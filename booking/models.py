from django.db import models
from django.contrib.auth.models import User, Group


class Course(models.Model):
    title = models.CharField(
        max_length=50,
        unique=True,
    )
    subject_code = models.CharField(
        max_length=10,
        unique=True,
    )
    students = models.ManyToManyField(
        User,
        limit_choices_to={'groups__name': "students"},
        related_name="enrolled_courses",
        blank=True,
    )
    assistant = models.ManyToManyField(
        User,
        limit_choices_to={'groups__name': "assistants"},
        related_name="assisting_courses",
        blank=True,
    )
    course_coordinator = models.OneToOneField(
        User,
        limit_choices_to={'groups__name': "course_coordinators"},
        default=None,
        on_delete=models.CASCADE,
        related_name="course"
    )

    def __str__(self):
        return self.title
