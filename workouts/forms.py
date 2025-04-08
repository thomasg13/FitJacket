from django import forms
from django.forms import inlineformset_factory

from .models import Workout, Exercise


class WorkoutForm(forms.ModelForm):
    class Meta:
        model = Workout
        fields = ['date']
        widgets = {
            'date': forms.DateInput(attrs={'type': 'date', 'class': 'form-control'})
        }

class ExerciseForm(forms.ModelForm):
    class Meta:
        model = Exercise
        fields = ['name', 'sets', 'reps']
        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-control'}),
            'sets': forms.NumberInput(attrs={'class': 'form-control', 'min': '1'}),
            'reps': forms.NumberInput(attrs={'class': 'form-control', 'min': '1'})
        }

# allows generating multiple ExerciseForms linked with a Workout
ExerciseFormSet = inlineformset_factory(
    Workout, Exercise,  # Workout is parent model, Exercise is child
    form=ExerciseForm,
    extra=0,
    can_delete=True,
    min_num=1,
    validate_min=True,
    max_num=25,  # maximum number of exercises
    validate_max=True  # validate maximum number
)