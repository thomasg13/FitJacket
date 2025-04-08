from django import forms
from .models import FitnessGoal

class FitnessGoalForm(forms.ModelForm):
    class Meta:
        model = FitnessGoal
        fields = ['water_intake', 'steps', 'calories']
        widgets = {
            'water_intake': forms.NumberInput(attrs={'class': 'form-control'}),
            'steps': forms.NumberInput(attrs={'class': 'form-control'}),
            'calories': forms.NumberInput(attrs={'class': 'form-control'}),
        }