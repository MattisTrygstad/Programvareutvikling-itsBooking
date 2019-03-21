from django.urls import path
from communications.views import *

urlpatterns = [
    path('<str:slug>/announcements/', AnnouncementListView.as_view(), name='announcements'),
]