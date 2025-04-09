from django.urls import path
from . import views

app_name = 'challenge'  # This registers the 'challenge' namespace

urlpatterns = [
    path('', views.challenge_list, name='challenge_list'),
    path('create/', views.create_challenge, name='create_challenge'),
]
