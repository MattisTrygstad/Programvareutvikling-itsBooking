from django.urls import path
from django.views.generic import ListView

from assignments.models import Exercise
from assignments.views import UploadExercise

urlpatterns = [
    path('<str:slug>/upload/', UploadExercise.as_view(), name='upload_exercise'),
    path('uploads/', ListView.as_view(model=Exercise), name='exercise_uploads_list'),
]