# Generated by Django 5.1.6 on 2025-04-06 17:19

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('roothub_app', '0005_announcement_read_by_alter_attendance_trainees_and_more'),
    ]

    operations = [
        migrations.AlterField(
            model_name='presentation',
            name='id',
            field=models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID'),
        ),
        migrations.AlterField(
            model_name='presentation_report',
            name='id',
            field=models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID'),
        ),
    ]
