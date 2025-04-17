from django.contrib import admin

# Register your models here.

from .models import WorkoutGroup

admin.site.register(WorkoutGroup)