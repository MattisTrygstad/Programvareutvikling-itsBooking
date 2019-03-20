from django.urls import path
from communications.views import *

urlpatterns = [
    path('<str:slug>/announcements/', AnnouncementView.as_view(), name='announcements'),
]