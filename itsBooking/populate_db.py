import random
from faker import Faker

from django.contrib.auth.models import Group, User
from django.core import management

from booking.models import Course

# flush db
management.call_command('flush', verbosity=0, interactive=False)
print("!----DB flushed----!")

#################
# setup base data
#################

# setup faker in norwegian
fake = Faker('no_NO')

# create groups
g_students = Group.objects.create(name='students')
g_assistants = Group.objects.create(name='assistants')
g_ccs = Group.objects.create(name='course_coordinators')

# create admin user
u_admin = User.objects.create_user(username='admin', password='123', is_staff=True, is_superuser=True)

# lists of users
students = []
assistants = []
ccs = []


def generate_users(group, group_list, number):
    username = str(group)[:-1]
    for i in range(len(group_list), len(group_list)+number):
        if i == 0:
            u = User.objects.create_user(username=username, password='123')
        else:
            u = User.objects.create_user(username=username+str(i), password='123')
        first_name, *last_name = fake.name().split(' ')
        u.first_name, u.last_name = first_name, ' '.join(last_name)
        u.email = fake.email()
        u.groups.add(group)
        group_list.append(u)
        u.save()


print("Generating users...")
generate_users(g_students, students, 10)
generate_users(g_assistants, assistants, 15)
generate_users(g_ccs, ccs, 2)

# create courses
c_algdat = Course.objects.create(title='Algoritmer og datastrukturer', course_code='TDT4120')
c_mat1 = Course.objects.create(title='Matematikk 1', course_code='TMA4100')
c_med = Course.objects.create(title='Innføring i medisin for ikke-medisinere', course_code='MFEL1010')

# add students to course
for student in students:
    c_algdat.students.add(student)

# add assistants to courses
for assistant in assistants:
    c_algdat.assistants.add(assistant)

# extra
c_algdat.course_coordinator = ccs[0]
c_mat1.students.add(students[0])
c_med.students.add(students[0])

print("Setting up courses...")
for bi in c_algdat.booking_intervals.all():
    r = random.randint(-1, 7)
    bi.min_available_assistants = r if r >= 0 else None
    for i in range(random.randint(0, r+1)):
        bi.assistants.add(random.choice(assistants))
    bi.save()


print("Saving new data...")
for v in list(locals().values()):
    try:
        v.save()
    except (AttributeError, TypeError):
        pass
print("DB successfully reset!")
