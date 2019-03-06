from django.urls import path
from booking.views import update_max_num_assistants, bi_registration_switch, CreateReservationView, student_reservation_list


urlpatterns = [
    path('reservation/<str:slug>/', CreateReservationView.as_view(), name='course_detail'),
    path('max_assistants/', update_max_num_assistants, name='update_max_num_assistants'),
    path('bi_registration_switch/', bi_registration_switch, name='bi_registration_switch'),
    path('reservations/', student_reservation_list, name='student_reservation_list'),
]
