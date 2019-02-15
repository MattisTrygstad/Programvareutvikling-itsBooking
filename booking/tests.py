from django.test import TestCase



from .models import Course, BookingInterval

# Create your tests here.

class CourseModelTest(TestCase):

    def test_create_course(self):
        """Initializes a Course-object without raising an exception"""
        try:
            course = Course(title="algdat", course_code="tdt4125")
            self.assertEqual(course.title, "algdat")
        except:  # Reminder: catch the exception
            self.fail("Failed initializing a course-object")

    def test_course_save(self):
        """Courses are assigned BookingInterval-objects when first saved"""
        course = Course(title="algdat", course_code="tdt4125")
        course.save()
        self.assertEqual(Course.objects
                         .filter(title="algdat").count(), 1)
        self.assertEqual(course.booking_intervals
                        .filter(course=course).count(), 25)
        # Checks that BookingInterval-objects are assigned only once
        course.save()
        self.assertEqual(course.booking_intervals
                         .filter(course=course).count(), 25)


