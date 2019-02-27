from django.urls import path

from booking.views import CreateReservationView, update_max_num_assistants

urlpatterns = [
    path('reservation/<str:slug>/', CreateReservationView.as_view(), name='course_detail'),
    path('max_assistants/', update_max_num_assistants, name='update_max_num_assistants'),
]
