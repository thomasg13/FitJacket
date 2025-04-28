from django import forms
from .models import WorkoutGroup

class WorkoutGroupForm(forms.ModelForm):
    class Meta:
        model = WorkoutGroup
        fields = ['name', 'description']