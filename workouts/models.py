from django.db import models
from django.contrib.auth.models import User

class Workout(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    date = models.DateField()

class Exercise(models.Model):
    EXERCISE_TYPES = [
        ('rep-based', 'Rep-based'),
        ('timed', 'Timed')
    ]
    
    workout = models.ForeignKey(Workout, on_delete=models.CASCADE)
    name = models.CharField(max_length=100)
    exercise_type = models.CharField(max_length=20, choices=EXERCISE_TYPES)
    weight = models.DecimalField(
        max_digits=5, decimal_places=2,
        null=True, blank=True,
        help_text="weight in pounds"
    )

    class Meta:
        abstract = True  # no table for this—just holds shared fields

class RepBasedExercise(Exercise):
    sets = models.PositiveIntegerField()
    reps = models.PositiveIntegerField()

    def clean(self):
        from django.core.exceptions import ValidationError
        if not (self.sets and self.reps):
            raise ValidationError("Need sets & reps for rep-based exercises")

class TimedExercise(Exercise):
    duration_minutes = models.PositiveIntegerField(null=True, blank=True)
    duration_seconds = models.PositiveIntegerField(null=True, blank=True)

    def clean(self):
        from django.core.exceptions import ValidationError
        # require at least some duration
        if not (self.duration_minutes or self.duration_seconds):
            raise ValidationError("Must set minutes or seconds for timed exercises")

    @property
    def total_seconds(self):
        mins = self.duration_minutes or 0
        secs = self.duration_seconds or 0
        return mins * 60 + secs