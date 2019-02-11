from django.db import models
from django.contrib.auth.models import User, Group

# Create your models here.
class Subject(models.Model):
    title=models.CharField(max_length=50, unique=True)
    subject_code=models.CharField(max_length=10, unique=True)
    students=models.ManyToManyField(User, limit_choices_to={'groups__name': "student"}, related_name="studenter",blank=True)
    assistant=models.ManyToManyField(User,limit_choices_to={'groups__name': "studass"}, related_name="studasser",blank=True)
    subject_coordinator = models.ForeignKey(User, limit_choices_to={'groups__name': "emne_ansvarlig"}, default = None, on_delete=models.CASCADE)

    def __str__(self):
        return self.title