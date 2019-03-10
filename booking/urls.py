import django.urls
from booking.views import update_max_num_assistants, bi_registration_switch, CreateReservationView, ReservationList, \
    AssistantReservationList


urlpatterns = [
    django.urls.path('reservation/<str:slug>/', CreateReservationView.as_view(), name='course_detail'),
    django.urls.path('max_assistants/', update_max_num_assistants, name='update_max_num_assistants'),
    django.urls.path('bi_registration_switch/', bi_registration_switch, name='bi_registration_switch'),
    django.urls.path('reservations/', ReservationList.as_view(), name='student_reservation_list'),
    django.urls.path('assistant_reservations/', AssistantReservationList.as_view(), name='assistant_reservation_list'),
]
