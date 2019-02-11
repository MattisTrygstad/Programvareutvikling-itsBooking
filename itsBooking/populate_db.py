from django.contrib.auth.models import Group, User
from django.core import management

# flush db
management.call_command('flush', verbosity=0, interactive=False)
print("!----DB flushed----!")

# setup base data
g1 = Group.objects.create(name='student')
g2 = Group.objects.create(name='studass')
g3 = Group.objects.create(name='emne_ansvarlig')

u1 = User.objects.create_user(username='admin', password='123', is_staff=True, is_superuser=True)

print("Saving new data...")
for v in list(locals().values()):
    try:
        v.save()
        print(f'{v} saved ({type(v)})')
    except (AttributeError, TypeError):
        pass
