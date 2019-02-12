# Generated by Django 2.0.12 on 2019-02-11 22:29

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('booking', '0001_initial'),
    ]

    operations = [
        migrations.RenameField(
            model_name='course',
            old_name='assistant',
            new_name='assistants',
        ),
        migrations.RenameField(
            model_name='course',
            old_name='subject_code',
            new_name='course_code',
        ),
        migrations.AlterField(
            model_name='course',
            name='course_coordinator',
            field=models.OneToOneField(blank=True, limit_choices_to={'groups__name': 'course_coordinators'}, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='course', to=settings.AUTH_USER_MODEL),
        ),
    ]
