from django.shortcuts import render

# Create your views here.
def goals_home(request):
    return render(request, 'goals/goals_home.html')