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
        fields = ['name', 'exercise_type', 'sets', 'reps', 'duration_minutes', 'duration_seconds']
        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-control'}),
            'exercise_type': forms.Select(attrs={'class': 'form-control exercise-type-select'}, choices=[('rep-based', 'Rep-based'), ('timed', 'Timed')]),
            'sets': forms.NumberInput(attrs={'class': 'form-control rep-based-field', 'min': '1'}),
            'reps': forms.NumberInput(attrs={'class': 'form-control rep-based-field', 'min': '1'}),
            'duration_minutes': forms.NumberInput(attrs={'class': 'form-control timed-field', 'min': '0'}),
            'duration_seconds': forms.NumberInput(attrs={'class': 'form-control timed-field', 'min': '0', 'max': '59'})
        }
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Set default exercise type to rep-based
        if not self.instance.pk:  # Only for new instances
            self.initial['exercise_type'] = 'rep-based'
        
        # Make exercise_type required
        self.fields['exercise_type'].required = True
        self.fields['exercise_type'].empty_label = None
    
    def clean(self):
        cleaned_data = super().clean()
        exercise_type = cleaned_data.get('exercise_type')
        
        # Validate based on exercise type
        if exercise_type == 'rep-based':
            if not cleaned_data.get('sets') or not cleaned_data.get('reps'):
                raise forms.ValidationError("Sets and reps are required for rep-based exercises.")
            # Clear timed fields
            cleaned_data['duration_minutes'] = None
            cleaned_data['duration_seconds'] = None
        elif exercise_type == 'timed':
            if not cleaned_data.get('duration_minutes') and not cleaned_data.get('duration_seconds'):
                raise forms.ValidationError("At least one duration field is required for timed exercises.")
            # Clear rep-based fields
            cleaned_data['sets'] = None
            cleaned_data['reps'] = None
        
        return cleaned_data

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