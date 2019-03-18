from django.shortcuts import render

class IndexView(generic.ListView):
    template_name = 'communications/announcements.html'
    context_object_name = 'announcement_list'

    def get_queryset(self):
        """Return the last five published announcements"""
        return Announcement.objects.filter(pub_date__lte=timezone.now()
                ).order_by('date_published')
