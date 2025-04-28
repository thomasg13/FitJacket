from django.urls import path
from . import views

app_name = 'socials'

urlpatterns = [
    path("", views.home, name='home'),
    path("search/", views.search_users, name="search_users"),
    path("friend-request/send/<int:user_id>/", views.send_friend_request, name="send_friend_request"),
    path("friend-request/accept/<int:request_id>/", views.accept_friend_request, name="accept_friend_request"),
]