from django.contrib.auth.models import User
from django.db.models import Count
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from .models import Challenge
from .forms import ChallengeForm

@login_required
def challenge_list(request):
    challenges = Challenge.objects.all()
    leaderboard = (
        User.objects
            .annotate(completed_count=Count('completed_challenges'))
            .filter(completed_count__gt=0)
            .order_by('-completed_count')[:10]
    )
    return render(request, 'challenge/challenge_list.html', {
        'challenges': challenges,
        'leaderboard': leaderboard,
    })


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

@login_required
def join_challenge(request, challenge_id):
    # Get the challenge object or 404 if it doesn't exist
    challenge = get_object_or_404(Challenge, id=challenge_id)

    # Add the user to the challenge participants
    challenge.participants.add(request.user)

    # Redirect back to the challenge list page
    return redirect('challenge:challenge_list')