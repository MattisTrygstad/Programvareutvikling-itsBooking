# Generated by Django 2.1.7 on 2019-03-11 15:48

import assignments.models
from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('booking', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='Exercise',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('file', models.FileField(upload_to=assignments.models.get_exercise_filepath)),
                ('review_text', models.TextField(blank=True, max_length=1500, null=True)),
                ('approved', models.BooleanField(blank=True, null=True)),
                ('course', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='exercise_uploads', to='booking.Course')),
                ('reviewed_by', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.DO_NOTHING, related_name='reviews', to=settings.AUTH_USER_MODEL)),
                ('student', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='exercises', to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'ordering': ['approved'],
            },
        ),
    ]
