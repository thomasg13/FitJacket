from django.urls import path
from . import views

app_name = 'goals'
urlpatterns = [
    path('', views.goals_home, name='goals_home'),
]