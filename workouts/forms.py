from django import forms
from django.forms import inlineformset_factory

from .models import Workout, RepBasedExercise, TimedExercise

class WorkoutForm(forms.ModelForm):
    class Meta:
        model = Workout
        fields = ['date']
        widgets = {
            'date': forms.DateInput(
                attrs={'type': 'date', 'class': 'form-control'}
            )
        }
    # nothing fancy here—the user just picks a date

class RepBasedExerciseForm(forms.ModelForm):
    class Meta:
        model = RepBasedExercise
        fields = ['name', 'sets', 'reps', 'weight']
        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-control'}),
            'sets': forms.NumberInput(attrs={'class': 'form-control', 'min': 1}),
            'reps': forms.NumberInput(attrs={'class': 'form-control', 'min': 1}),
            'weight': forms.NumberInput(
                attrs={'class': 'form-control', 'min': 0, 'step': 0.5}
            ),
        }
    # no need for a custom __init__; fields map 1:1 with the model

class TimedExerciseForm(forms.ModelForm):
    class Meta:
        model = TimedExercise
        fields = ['name', 'duration_minutes', 'duration_seconds']
        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-control'}),
            'duration_minutes': forms.NumberInput(
                attrs={'class': 'form-control', 'min': 0}
            ),
            'duration_seconds': forms.NumberInput(
                attrs={'class': 'form-control', 'min': 0, 'max': 59}
            ),
        }

    def clean(self):
        cleaned = super().clean()
        # gotta have at least one timing field
        if not (cleaned.get('duration_minutes') or cleaned.get('duration_seconds')):
            raise forms.ValidationError(
                "Set minutes or seconds for a timed exercise."
            )
        return cleaned

# two inline formsets—one for each concrete strategy
RepBasedExerciseFormSet = inlineformset_factory(
    Workout,
    RepBasedExercise,
    form=RepBasedExerciseForm,
    extra=1,
    can_delete=True,
    max_num=25,
    validate_max=True,
)

TimedExerciseFormSet = inlineformset_factory(
    Workout,
    TimedExercise,
    form=TimedExerciseForm,
    extra=1,
    can_delete=True,
    max_num=25,
    validate_max=True,
)