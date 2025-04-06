from django.urls import path
from . import views
from django.contrib.auth import views as auth_views


app_name = 'users'

urlpatterns = [
    path('login/', views.login_view, name='login'),
    path('logout/', views.logout_view, name='logout'),
    path('signup/', views.signup_view, name='signup'),


    path('forgot_password/', views.forgot_password_view, name='forgot_password'),
    path('password_reset_confirm/', views.password_reset_confirm_view, name='password_reset_confirm'),
]