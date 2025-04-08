from django.contrib import admin
from django.urls import path

from django.contrib import admin
from django.urls import path, include
from django.contrib.auth import views as auth_views
# Import include

urlpatterns = [
    path('admin/', admin.site.urls),  # Default Django admin site
    path('', include('home.urls')),
    path("users/", include('users.urls')),
    path("workouts/", include('workouts.urls')),
    path('goals/', include('goals.urls')),
]