from django.urls import path
from . import views

app_name = 'groups'
urlpatterns = [
    path('', views.workout_groups, name='workout_groups'),
    path('create/', views.create_group, name='create_group'),
    path('<int:group_id>/', views.group_detail, name='group_detail'),
    path('<int:group_id>/join/', views.join_group, name='join_group'),
    path('<int:group_id>/leave/', views.leave_group, name='leave_group'),
    path('<int:group_id>/create_challenge/', views.create_challenge, name='create_challenge'),
    path('<int:group_id>/challenge/<int:challenge_id>/join/', views.join_challenge, name='join_challenge'),
    path('<int:group_id>/challenge/<int:challenge_id>/leave/', views.leave_challenge, name='leave_challenge'),
    path('<int:group_id>/challenge/<int:challenge_id>/complete/', views.complete_challenge, name='complete_challenge'),
]

