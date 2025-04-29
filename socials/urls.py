from django.urls import path
from . import views

app_name = 'socials'

urlpatterns = [
    path("", views.home, name='home'),
    path("search/", views.search_users, name="search_users"),
    path("friend-request/send/<int:user_id>/", views.send_friend_request, name="send_friend_request"),
    path("friend-request/accept/<int:request_id>/", views.accept_friend_request, name="accept_friend_request"),
    path('unfriend/<int:user_id>/', views.unfriend, name='unfriend'),
    path('cancel_request/<int:request_id>/', views.cancel_friend_request, name='cancel_friend_request'),
    path('reject_request/<int:request_id>/', views.reject_friend_request, name='reject_friend_request'),
    path('profile/<int:user_id>/', views.friend_profile, name='friend_profile'),
]