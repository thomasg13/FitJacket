from django.urls import path
from . import views

app_name = 'groups'
urlpatterns = [
    path('', views.workout_groups, name='workout_groups_list'),
    path('join/<int:group_id>/', views.join_group, name='join_group'),
    path('leave/<int:group_id>/', views.leave_group, name='leave_group'),
    path('groups/', views.workout_groups_view, name='workout_groups_list'),
    path('create/', views.create_group, name='create_group'),
]

