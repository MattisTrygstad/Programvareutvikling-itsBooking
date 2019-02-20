from django.urls import path

from booking.views import CourseDetail, update_min_num_assistants, StudentBooking

urlpatterns = [
    path('test/<str:slug>/', StudentBooking.as_view(), name="test"),
    path('<str:slug>/', CourseDetail.as_view(), name='course_detail'),
    path('update', update_min_num_assistants, name='update_min_num_assistants'),
]
