from django.db import models
from django.contrib.auth.models import User

class UserProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name="profile")
    security_question = models.CharField(max_length=50, choices=[
        ("q1", "What is your favorite color?"),
        ("q2", "What is your first pet’s name?"),
        ("q3", "What is your mother's maiden name?"),
    ])
    security_answer = models.CharField(max_length=150)  # Store answers case-insensitively

    def save(self, *args, **kwargs):
        # lowercase the answer to make check easier
        self.security_answer = self.security_answer.lower()
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.user.username}'s Profile"