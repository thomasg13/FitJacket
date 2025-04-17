from django.db import models
from django.contrib.auth.models import User
# Create your models here.

class WorkoutGroup(models.Model):
    name = models.CharField(max_length=100)
    description = models.TextField()
    members = models.ManyToManyField(User, related_name='joined_workout_groups')

    def __str__(self):
        return self.name