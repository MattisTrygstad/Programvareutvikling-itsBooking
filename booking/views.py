from django.views.generic import DetailView

from booking.models import Course


class CourseDetail(DetailView):
    model = Course

