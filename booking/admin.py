from django.contrib import admin
from .models import Course, BookingInterval, Reservation


class CourseAdmin(admin.ModelAdmin):
    prepopulated_fields = {"slug": ("course_code",)}


admin.site.register(Course, CourseAdmin)
admin.site.register(BookingInterval)
admin.site.register(Reservation)
