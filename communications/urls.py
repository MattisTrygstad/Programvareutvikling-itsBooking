from django.urls import path
from communications.views import *

urlpatterns = [
    path('<str:slug>/announcements/', AnnouncementListView.as_view(), name='announcements'),
    path('/announcements/<int:pk>/delete', DeleteAnnouncementView.as_view(), name='delete_announcement'),
]
