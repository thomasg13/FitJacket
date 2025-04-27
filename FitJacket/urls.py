from django.contrib import admin
from django.urls import path, include

urlpatterns = [
    path('admin/', admin.site.urls),  # Default Django admin site
    path('', include('home.urls')),
    path("users/", include('users.urls')),
    path("workouts/", include('workouts.urls')),
    path('goals/', include('goals.urls')),
    path('challenge/', include(('challenge.urls', 'challenge'), namespace='challenge')),
    path('groups/', include('groups.urls', namespace='groups')),
    path('workout_stats/', include(('workout_stats.urls', 'workout_stats'), namespace='workout_stats')),
]