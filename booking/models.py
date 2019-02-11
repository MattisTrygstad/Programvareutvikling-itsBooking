from django.db import models
from django.contrib.auth.models import User, Group

# Create your models here.
class Emne(models.Model):
    title=models.CharField(max_length=50, unique=True)
    course_code=models.CharField(max_length=10, unique=True)
    studenter=models.ManyToManyField(User,limit_choices_to={'groups__name': "student"},related_name="studenter",blank=True)
    studasser=models.ManyToManyField(User,limit_choices_to={'groups__name': "studass"},related_name="studasser",blank=True)
    emneansvarlig = models.ForeignKey(User,limit_choices_to={'groups__name': "emne_ansvarlig"}, default = 0, on_delete=models.CASCADE)

    def __str__(self):
        return self.title