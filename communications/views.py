from django.shortcuts import render
from communications.models import Announcement
from django.utils import timezone
from django.views.generic.list import ListView
from django.views import generic
from django.contrib.auth.models import User
from django.db import models

class IndexView(generic.ListView):
    template_name = 'communications/announcements.html'
    context_object_name = 'announcement_list'

    def get_queryset(self):
        """Return the last five published announcements"""
        return Announcement.objects.all()
