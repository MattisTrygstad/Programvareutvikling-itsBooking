from django.urls import path
from django.views.generic import ListView

from assignments.models import Exercise
from assignments.views import UploadExercise, ExerciseList

urlpatterns = [
    path('<str:slug>/upload/', UploadExercise.as_view(), name='upload_exercise'),
    path('<str:slug>/uploads/', ExerciseList.as_view(), name='exercise_uploads_list'),
]