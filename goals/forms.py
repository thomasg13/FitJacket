from django import forms
from .models import FitnessGoal

class FitnessGoalForm(forms.ModelForm):
    class Meta:
        model = FitnessGoal
        fields = ['weekly_miles_goal', 'weekly_workout_days_goal', 'daily_steps', 'daily_calories']
        widgets = {
            'weekly_miles_goal': forms.NumberInput(attrs={'class': 'form-control'}),
            'weekly_workout_days_goal': forms.NumberInput(attrs={'class': 'form-control'}),
            'daily_steps': forms.NumberInput(attrs={'class': 'form-control'}),
            'daily_calories': forms.NumberInput(attrs={'class': 'form-control'}),
        }