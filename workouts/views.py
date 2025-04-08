from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from .models import Workout
from workouts.forms import WorkoutForm, ExerciseFormSet


@login_required()
def workout_list(req):
    workouts = Workout.objects.filter(user=req.user).order_by('-date')

    return render(req, 'workouts/workout_list.html', {
        'workouts': workouts
    })

@login_required() #redirects user to login if they aren't
def create_workout_with_exercises(req):
    user = req.user

    if req.method == 'POST':
        workout_form = WorkoutForm(req.POST)
        formset = ExerciseFormSet(req.POST)

        if workout_form.is_valid() and formset.is_valid():
            workout = workout_form.save(commit=False)
            workout.user = user
            workout.save()

            exercises = formset.save(commit=False)
            for exercise in exercises:
                exercise.workout = workout
                exercise.save()

            return redirect('workouts:workout_list')
    else:
        workout_form = WorkoutForm()
        formset = ExerciseFormSet()

    return render(req, 'workouts/workout_form.html', {
        'workout_form': workout_form,
        'formset': formset
    })

@login_required()
def edit_workout(req, workout_id):
    workout = get_object_or_404(Workout, id=workout_id, user=req.user)
    
    if req.method == 'POST':
        workout_form = WorkoutForm(req.POST, instance=workout)
        formset = ExerciseFormSet(req.POST, instance=workout)
        
        if workout_form.is_valid() and formset.is_valid():
            workout = workout_form.save()
            formset.save()
            messages.success(req, 'Workout updated successfully!')
            return redirect('workouts:workout_list')
    else:
        workout_form = WorkoutForm(instance=workout)
        formset = ExerciseFormSet(instance=workout)
    
    return render(req, 'workouts/workout_form.html', {
        'workout_form': workout_form,
        'formset': formset,
        'workout': workout,
        'is_edit': True
    })

@login_required
def delete_workout(request, workout_id):
    workout = get_object_or_404(Workout, id=workout_id, user=request.user)
    if request.method == 'POST':
        workout.delete()
        messages.success(request, 'Workout deleted successfully!')
    return redirect('workouts:workout_list')