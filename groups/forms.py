from django import forms
from .models import WorkoutGroup, Challenge

class WorkoutGroupForm(forms.ModelForm):
    class Meta:
        model = WorkoutGroup
        fields = ['name', 'description']

class ChallengeForm(forms.ModelForm):
    class Meta:
        model = Challenge
        fields = ['title', 'description']