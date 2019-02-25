from django.urls import path
from django.conf.urls import url
from booking.views import CourseDetail, update_min_num_assistants, make_assistants_available

urlpatterns = [
    path('<str:slug>/', CourseDetail.as_view(), name='course_detail'),
    path('update', update_min_num_assistants, name='update_min_num_assistants'),
    url('make_available', make_assistants_available, name='make_assistants_available'),
]
