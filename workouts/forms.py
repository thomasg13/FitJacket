from django import forms
from django.forms import inlineformset_factory
from .models import Workout, RepBasedExercise, TimedExercise, ExerciseFactory

class WorkoutForm(forms.ModelForm):
    class Meta:
        model = Workout
        fields = ['date']
        widgets = {
            'date': forms.DateInput(attrs={'type': 'date', 'class': 'form-control'})
        }

class BaseExerciseForm(forms.ModelForm):
    class Meta:
        fields = ['name', 'weight']
        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-control'}),
            'weight': forms.NumberInput(
                attrs={'class': 'form-control', 'min': 0, 'step': 0.5}
            ),
        }

class RepBasedExerciseForm(BaseExerciseForm):
    class Meta(BaseExerciseForm.Meta):
        model = RepBasedExercise
        fields = BaseExerciseForm.Meta.fields + ['sets', 'reps']
        widgets = {
            **BaseExerciseForm.Meta.widgets,
            'sets': forms.NumberInput(attrs={'class': 'form-control', 'min': 1}),
            'reps': forms.NumberInput(attrs={'class': 'form-control', 'min': 1}),
        }

    def save(self, commit=True):
        instance = super().save(commit=False)
        instance.exercise_type = 'rep-based'
        if commit:
            instance.save()
        return instance

class TimedExerciseForm(BaseExerciseForm):
    class Meta(BaseExerciseForm.Meta):
        model = TimedExercise
        fields = BaseExerciseForm.Meta.fields + ['duration_minutes', 'duration_seconds']
        widgets = {
            **BaseExerciseForm.Meta.widgets,
            'duration_minutes': forms.NumberInput(
                attrs={'class': 'form-control', 'min': 0}
            ),
            'duration_seconds': forms.NumberInput(
                attrs={'class': 'form-control', 'min': 0, 'max': 59}
            ),
        }

    def clean(self):
        cleaned = super().clean()
        if not (cleaned.get('duration_minutes') or cleaned.get('duration_seconds')):
            raise forms.ValidationError(
                "Set minutes or seconds for a timed exercise."
            )
        return cleaned

    def save(self, commit=True):
        instance = super().save(commit=False)
        instance.exercise_type = 'timed'
        if commit:
            instance.save()
        return instance

class ExerciseFormFactory:
    @staticmethod
    def create_form(exercise_type, **kwargs):
        if exercise_type == 'rep-based':
            return RepBasedExerciseForm(**kwargs)
        elif exercise_type == 'timed':
            return TimedExerciseForm(**kwargs)
        else:
            raise ValueError(f"Invalid exercise type: {exercise_type}")

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