from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone
# Create your models here.

class WorkoutGroup(models.Model):
    name = models.CharField(max_length=100)
    description = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    members = models.ManyToManyField(User, related_name='workout_groups')

class Challenge(models.Model):
    title = models.CharField(max_length=100)
    description = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    group = models.ForeignKey(WorkoutGroup, on_delete=models.CASCADE, related_name='challenges')
    participants = models.ManyToManyField(User, related_name='challenges')
    completed = models.BooleanField(default=False)

    class Meta:
        ordering = ['-created_at']