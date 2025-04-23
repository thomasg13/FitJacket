from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.utils import timezone
from .models import Workout, ExerciseFactory, StravaAccount
from workouts.forms import WorkoutForm, ExerciseFormFactory, RepBasedExerciseFormSet, TimedExerciseFormSet
import logging
from openai import OpenAI
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
import json
import requests
from datetime import datetime, timedelta
import pytz
from config.config_manager import ConfigurationManager

logger = logging.getLogger(__name__)
config = ConfigurationManager()

# Load all needed configurations at startup
strava_client_id = config.get("STRAVA_CLIENT_ID")
strava_client_secret = config.get("STRAVA_CLIENT_SECRET")
strava_redirect_uri = config.get("STRAVA_REDIRECT_URI")
openai_key = config.get("OPENAI_API_KEY")
client = OpenAI(api_key=openai_key)

def create_exercises(workout, exercise_data, exercise_type):
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

def get_strava_auth_url():
    params = {
        'client_id': strava_client_id,
        'redirect_uri': strava_redirect_uri,
        'response_type': 'code',
        'scope': 'activity:read_all'
    }
    return f"https://www.strava.com/oauth/authorize?{'&'.join(f'{k}={v}' for k, v in params.items())}"

@login_required
def strava_auth(request):
    return redirect(get_strava_auth_url())

@login_required
def strava_callback(request):
    code = request.GET.get('code')
    if not code:
        messages.error(request, 'Failed to connect to Strava')
        return redirect('workouts:create_workout')

    response = requests.post('https://www.strava.com/oauth/token', data={
        'client_id': strava_client_id,
        'client_secret': strava_client_secret,
        'code': code,
        'grant_type': 'authorization_code'
    })

    if response.status_code != 200:
        messages.error(request, 'Failed to connect to Strava')
        return redirect('workouts:create_workout')

    data = response.json()
    
    StravaAccount.objects.update_or_create(
        user=request.user,
        defaults={
            'access_token': data['access_token'],
            'refresh_token': data['refresh_token'],
            'token_expires_at': datetime.fromtimestamp(data['expires_at'], tz=pytz.UTC),
            'athlete_id': str(data['athlete']['id'])
        }
    )

    messages.success(request, 'Successfully connected to Strava!')
    return redirect('workouts:create_workout')

@login_required
def import_strava_workout(request):
    try:
        strava_account = StravaAccount.objects.get(user=request.user)
    except StravaAccount.DoesNotExist:
        return JsonResponse({'error': 'Please connect your Strava account first'}, status=400)
    
    # Check if token needs refresh
    now = timezone.now()
    if strava_account.token_expires_at <= now:
        response = requests.post('https://www.strava.com/oauth/token', data={
            'client_id': strava_client_id,
            'client_secret': strava_client_secret,
            'refresh_token': strava_account.refresh_token,
            'grant_type': 'refresh_token'
        })

        if response.status_code != 200:
            return JsonResponse({'error': 'Failed to refresh Strava token'}, status=400)

        data = response.json()
        strava_account.access_token = data['access_token']
        strava_account.refresh_token = data['refresh_token']
        strava_account.token_expires_at = datetime.fromtimestamp(data['expires_at'], tz=pytz.UTC)
        strava_account.save()

    # Get latest activity
    headers = {'Authorization': f'Bearer {strava_account.access_token}'}
    response = requests.get('https://www.strava.com/api/v3/athlete/activities', 
                          headers=headers, 
                          params={'per_page': 1})

    if response.status_code != 200:
        return JsonResponse({'error': 'Failed to fetch Strava activity'}, status=400)

    activities = response.json()
    if not activities:
        return JsonResponse({'error': 'No recent Strava activities found'}, status=400)

    activity = activities[0]
    
    if Workout.objects.filter(strava_id=str(activity['id'])).exists():
        return JsonResponse({'error': 'This Strava activity has already been imported'}, status=400)

    workout = Workout.objects.create(
        user=request.user,
        date=datetime.strptime(activity['start_date'][:10], '%Y-%m-%d').date(),
        strava_id=str(activity['id'])
    )

    if activity['type'] in ['Run', 'Walk']:
        exercise = ExerciseFactory.create_exercise('timed', 
            workout=workout,
            name=activity['name'],
            duration_minutes=int(activity['moving_time'] // 60),
            duration_seconds=int(activity['moving_time'] % 60),
            distance=round(activity['distance'] / 1609.34, 2)  # Convert meters to miles
        )
        exercise.save()
    
    return JsonResponse({
        'success': True,
        'message': 'Successfully imported Strava activity',
        'workout_id': workout.id
    })

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
                    data = form.cleaned_data.copy()
                    data['workout'] = workout
                    exercise = ExerciseFactory.create_exercise('rep-based', **data)
                    exercise.save()

            # Save timed exercises
            for form in timed_formset:
                if form.cleaned_data and not form.cleaned_data.get('DELETE', False):
                    data = form.cleaned_data.copy()
                    data['workout'] = workout
                    exercise = ExerciseFactory.create_exercise('timed', **data)
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
                ],
                max_tokens=150,
                temperature=0.7
            )
            reply = response.choices[0].message.content.strip()
            return JsonResponse({"reply": reply})

        except Exception as e:
            logger.error(f"ChatBot error: {str(e)}")
            return JsonResponse({"reply": f"Error: {str(e)}"})

    return JsonResponse({"reply": "Invalid request method."})
