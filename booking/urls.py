from django.urls import path

from booking.views import CourseDetail

urlpatterns = [
    path('<str:slug>/', CourseDetail.as_view(), name='course_detail'),
]
