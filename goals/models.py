from django.db import models
from django.contrib.auth.models import User

# Create your models here.
class FitnessGoal(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    weekly_miles_goal = models.DecimalField(max_digits=5, decimal_places=1, default=10)
    weekly_workout_days_goal = models.IntegerField(default=4)
    daily_steps = models.PositiveIntegerField(default=10000)
    daily_calories = models.PositiveIntegerField(default=2000)