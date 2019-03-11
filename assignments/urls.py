from django.urls import path
from django.views.generic import ListView

from assignments.models import Exercise
from assignments.views import UploadExercise, CourseExerciseList, StudentExerciseList

urlpatterns = [
    path('<str:slug>/upload/', UploadExercise.as_view(), name='upload_exercise'),
    path('<str:slug>/uploads/', CourseExerciseList.as_view(), name='exercise_uploads_list'),
    path('<str:slug>/uploads/', StudentExerciseList.as_view(), name='exercise_uploads_list'),
]