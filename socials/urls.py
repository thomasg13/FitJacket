from django.urls import path
from . import views

app_name = 'socials'

urlpatterns = [
    path("", views.home, name='home'),
]