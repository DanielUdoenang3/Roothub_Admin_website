from django.contrib import admin

# Register your models here.
from django.contrib.auth.admin import UserAdmin

from roothub_app.models import *

class UserModel(UserAdmin):
    pass

