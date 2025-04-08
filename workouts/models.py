from django.db import models

from django.contrib.auth.models import User


class Workout(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    date = models.DateField()

class Exercise(models.Model):
    workout = models.ForeignKey(Workout, related_name='exercises', on_delete=models.CASCADE)
    name = models.CharField(max_length=100)
    exercise_type = models.CharField(max_length=20, choices=[('rep-based', 'Rep-based'), ('timed', 'Timed')])
    
    # rep-based fields
    sets = models.PositiveIntegerField(null=True, blank=True)
    reps = models.PositiveIntegerField(null=True, blank=True)
    
    # timed fields
    duration_minutes = models.PositiveIntegerField(null=True, blank=True)
    duration_seconds = models.PositiveIntegerField(null=True, blank=True)
    
    def clean(self):
        from django.core.exceptions import ValidationError
        
        # validate that rep-based or timed fields are filled based on exercise_type
        if self.exercise_type == 'rep-based':
            if not self.sets or not self.reps:
                raise ValidationError("Sets and reps are required for rep-based exercises.")
            if self.duration_minutes or self.duration_seconds:
                raise ValidationError("Duration fields should not be set for rep-based exercises.")
        elif self.exercise_type == 'timed':
            if not (self.duration_minutes or self.duration_seconds):
                raise ValidationError("At least one duration field is required for timed exercises.")
            if self.sets or self.reps:
                raise ValidationError("Sets and reps should not be set for timed exercises.")
