from django.contrib import admin
from .models import UserProfile

@admin.register(UserProfile)
class UserProfileAdmin(admin.ModelAdmin):
    list_display = ("user", "security_question", "security_answer")  # Display these fields in the admin panel
    search_fields = ("user__username", "security_question")  # Add search functionality
