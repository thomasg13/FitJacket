from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from .models import Challenge
from .forms import ChallengeForm

@login_required
def challenge_list(request):
    challenges = Challenge.objects.all()
    return render(request, 'challenge/challenge_list.html', {'challenges': challenges})

@login_required
def create_challenge(request):
    if request.method == 'POST':
        form = ChallengeForm(request.POST)
        if form.is_valid():
            challenge = form.save(commit=False)
            challenge.creator = request.user
            challenge.save()
            return redirect('challenge:challenge_list')
    else:
        form = ChallengeForm()
    return render(request, 'challenge/create_challenge.html', {'form': form})
