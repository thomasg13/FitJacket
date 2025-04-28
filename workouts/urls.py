from django.urls import path
from . import views

app_name = 'workouts'

urlpatterns = [
    path('', views.workout_list, name='workout_list'),
    path('new/', views.create_workout, name='create_workout'),
    path('<int:workout_id>/delete/', views.delete_workout, name='delete_workout'),
    
    path('chatbot/', views.chatbot_view, name='chatbot'),

    # Strava URLs
    path('strava/connect/', views.strava_auth, name='strava_connect'),  # Initiates Strava OAuth
    path('strava/callback/', views.strava_callback, name='strava_callback'),  # Where Strava redirects back to
    path('strava/import/', views.import_strava_workout, name='strava_import'),  # Endpoint for importing Strava workouts

    path('get_recent_workouts/', views.get_recent_workouts, name='get_recent_workouts'),
]