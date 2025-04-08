from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect

from goals.forms import FitnessGoalForm
from goals.models import FitnessGoal


# Create your views here.
@login_required
def goals_home(request):
    goal, created = FitnessGoal.objects.get_or_create(user=request.user)

    if request.method == 'POST':
        form = FitnessGoalForm(request.POST, instance=goal)
        if form.is_valid():
            form.save()
            return redirect('goals:goals_home')
    else:
        form = FitnessGoalForm(instance=goal)

    return render(request, 'goals/goals_home.html', {'form': form, 'goal': goal})