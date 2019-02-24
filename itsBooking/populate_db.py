from django.contrib.auth.models import Group, User
from django.core import management

from booking.models import Course

# flush db
management.call_command('flush', verbosity=0, interactive=False)
print("!----DB flushed----!")

#################
# setup base data
#################

# create groups
g_students = Group.objects.create(name='students')
g_assistants = Group.objects.create(name='assistants')
g_ccs = Group.objects.create(name='course_coordinators')

# create users, add users to their respective groups
u_admin = User.objects.create_user(username='admin', password='123', is_staff=True, is_superuser=True)
u_student_1 = User.objects.create_user(username='student', password='123')
u_assistant_1 = User.objects.create_user(username='assistant', password='123')
u_assistant_2 = User.objects.create_user(username='assistant2', password='123')
u_cc_1 = User.objects.create_user(username='cc', password='123')
u_student_1.groups.add(g_students)
u_assistant_1.groups.add(g_assistants)
u_assistant_2.groups.add(g_assistants)
u_cc_1.groups.add(g_ccs)

# create courses
c_algdat = Course.objects.create(title='Algoritmer og datastrukturer', course_code='TDT4120')
c_mat1 = Course.objects.create(title='Matematikk 1', course_code='TMA4100')
c_med = Course.objects.create(title='Innføring i medisin for ikke-medisinere', course_code='MFEL1010')

# add users to courses
c_algdat.students.add(u_student_1)
c_algdat.assistants.add(u_assistant_1)
c_algdat.assistants.add(u_assistant_2)

c_algdat.course_coordinator = u_cc_1

c_mat1.students.add(u_student_1)
c_mat1.assistants.add(u_assistant_1)

c_med.students.add(u_student_1)

print("Saving new data...")
for v in list(locals().values()):
    try:
        v.save()
    except (AttributeError, TypeError):
        pass
print("DB successfully reset!")
