from django.db import models
from django.contrib.auth.models import User

# Create your models here.
class FitnessGoal(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    weekly_miles_goal = models.DecimalField(max_digits=5, decimal_places=1, default=0)
    weekly_workout_days_goal = models.IntegerField(default=0)
    daily_steps = models.PositiveIntegerField(default=0)
    daily_calories = models.PositiveIntegerField(default=0)