# Generated by Django 5.1.2 on 2025-03-30 16:33

from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('roothub_app', '0003_alter_attendancereport_student_id'),
    ]

    operations = [
        migrations.AlterField(
            model_name='attendance',
            name='trainees',
            field=models.ManyToManyField(related_name='attendance_records', to=settings.AUTH_USER_MODEL),
        ),
    ]
