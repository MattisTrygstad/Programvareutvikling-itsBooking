from django.urls import path
from django.views.generic import ListView

from communications.models import Announcement
from communications.views import *

urlpatterns = [
    path('<str:slug>/announcements/', AnnouncementView.as_view(), name='announcements'),
]