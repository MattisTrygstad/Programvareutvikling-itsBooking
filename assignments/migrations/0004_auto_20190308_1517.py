# Generated by Django 2.1.7 on 2019-03-08 14:17

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('assignments', '0003_auto_20190308_1516'),
    ]

    operations = [
        migrations.AlterField(
            model_name='exercise',
            name='student',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='assignments', to=settings.AUTH_USER_MODEL),
        ),
    ]
