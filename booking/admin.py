from django.contrib import admin
from .models import Course, BookingInterval, ReservationInterval, ReservationConnection


class CourseAdmin(admin.ModelAdmin):
    prepopulated_fields = {"slug": ("course_code",)}


class BookingIntervalAdmin(admin.ModelAdmin):
    readonly_fields = ('nk', 'day', 'start', 'end', 'course', )


class ReservationIntervalAdmin(admin.ModelAdmin):
    readonly_fields = ('booking_interval', )


admin.site.register(Course, CourseAdmin)
admin.site.register(BookingInterval, BookingIntervalAdmin)
admin.site.register(ReservationInterval, ReservationIntervalAdmin)
admin.site.register(ReservationConnection)
