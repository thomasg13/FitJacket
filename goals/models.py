from django.db import models
from django.contrib.auth.models import User

# Create your models here.
class FitnessGoal(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    water_intake = models.PositiveIntegerField(default=0, help_text="oz per day")
    steps = models.PositiveIntegerField(default=0)
    calories = models.PositiveIntegerField(default=0)

    def __str__(self):
        return f"{self.user.username}'s goals"
