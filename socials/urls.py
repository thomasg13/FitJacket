from django.urls import path
from . import views

app_name = 'socials'

urlpatterns = [
    path("", views.home, name='home'),
    path("search/", views.search_users, name="search_users"),
]