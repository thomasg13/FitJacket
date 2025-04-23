from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from .models import Workout, ExerciseFactory
from workouts.forms import WorkoutForm, ExerciseFormFactory, RepBasedExerciseFormSet, TimedExerciseFormSet
import logging
from openai import OpenAI
from django.conf import settings
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
import json

logger = logging.getLogger(__name__)
client = OpenAI(api_key=settings.OPENAI_API_KEY)

def create_exercises(workout, exercise_data, exercise_type):
    """Helper function to create exercises using the factory pattern"""
    for data in exercise_data:
        if data.get('name'):  # Only create if there's a name
            form = ExerciseFormFactory.create_form(
                exercise_type=exercise_type,
                data=data
            )
            if form.is_valid():
                exercise = form.save(commit=False)
                exercise.workout = workout
                exercise.save()

@login_required()
def workout_list(req):
    workouts = Workout.objects.filter(user=req.user).order_by('-date')
    return render(req, 'workouts/workout_list.html', {
        'workouts': workouts
    })

@login_required()
def create_workout(req):
    if req.method == 'POST':
        workout_form = WorkoutForm(req.POST)
        rep_formset = RepBasedExerciseFormSet(req.POST, prefix='rep')
        timed_formset = TimedExerciseFormSet(req.POST, prefix='timed')

        if (workout_form.is_valid() and rep_formset.is_valid()
                and timed_formset.is_valid()):
            workout = workout_form.save(commit=False)
            workout.user = req.user
            workout.save()

            # Save rep-based exercises
            for form in rep_formset:
                if form.cleaned_data and not form.cleaned_data.get('DELETE', False):
                    exercise = form.save(commit=False)
                    exercise.workout = workout
                    exercise.exercise_type = 'rep-based'
                    exercise.save()

            # Save timed exercises
            for form in timed_formset:
                if form.cleaned_data and not form.cleaned_data.get('DELETE', False):
                    exercise = form.save(commit=False)
                    exercise.workout = workout
                    exercise.exercise_type = 'timed'
                    exercise.save()

            return redirect('workouts:workout_list')
    else:
        workout_form = WorkoutForm()
        rep_formset = RepBasedExerciseFormSet(prefix='rep')
        timed_formset = TimedExerciseFormSet(prefix='timed')

    return render(req, 'workouts/workout_form.html', {
        'workout_form': workout_form,
        'rep_formset': rep_formset,
        'timed_formset': timed_formset
    })

@login_required
def delete_workout(request, workout_id):
    workout = get_object_or_404(Workout, id=workout_id, user=request.user)
    if request.method == 'POST':
        workout.delete()
        messages.success(request, 'Workout deleted successfully!')
        return redirect('workouts:workout_list')
    return render(request, 'workouts/workout_confirm_delete.html', {'workout': workout})

@csrf_exempt
def chatbot_view(request):
    if request.method == "POST":
        data = json.loads(request.body)
        user_message = data.get("message", "")

        try:
            response = client.chat.completions.create(
                model="gpt-3.5-turbo",
                messages=[
                    {"role": "system", "content": "You are a helpful fitness assistant named FitBot."},
                    {"role": "user", "content": user_message}
                ]
            )
            reply = response.choices[0].message.content.strip()
            return JsonResponse({"reply": reply})

        except Exception as e:
            return JsonResponse({"reply": f"Error: {str(e)}"})

    return JsonResponse({"reply": "Invalid request method."})
