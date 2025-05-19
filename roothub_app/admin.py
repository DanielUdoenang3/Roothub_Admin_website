from django.contrib import admin

# Register your models here.
from django.contrib.auth.admin import UserAdmin

from roothub_app.models import *

class CustomUserAdmin(UserAdmin):
    pass

admin.site.register(CustomUser, CustomUserAdmin)
admin.site.register(Admin)
admin.site.register(Trainers)
admin.site.register(Trainee)
admin.site.register(Courses)
admin.site.register(Attendance)
admin.site.register(Presentation)
admin.site.register(Presentation_report)
admin.site.register(AttendanceReport)
admin.site.register(FeedBackStudent)
admin.site.register(FeedBackTrainer)
admin.site.register(NotificationStudent)
admin.site.register(NotificationTrainer)
admin.site.register(Assignment)
admin.site.register(AssignmentSubmission)
admin.site.register(Announcement)
admin.site.register(Fix_Class)