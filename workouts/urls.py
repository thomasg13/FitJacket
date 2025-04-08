from django.urls import path
from . import views

app_name = 'workouts'

urlpatterns = [
    path('new/', views.create_workout_with_exercises, name='create_workout'),
    path('<int:workout_id>/edit/', views.edit_workout, name='edit_workout'),
    path('<int:workout_id>/delete/', views.delete_workout, name='delete_workout'),
    path('', views.workout_list, name='workout_list'),
]