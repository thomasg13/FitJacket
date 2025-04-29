# Create your views here.
from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from .models import WorkoutGroup, Challenge
from .forms import WorkoutGroupForm, ChallengeForm
from django.contrib import messages


@login_required
def workout_groups(request):
    groups = WorkoutGroup.objects.all()
    user_groups = groups.filter(members=request.user)
    available_groups = groups.exclude(members=request.user)
    return render(request, 'groups/workout_groups.html', {
        'user_groups': user_groups,
        'available_groups': available_groups
    })

@login_required
def join_group(request, group_id):
    group = get_object_or_404(WorkoutGroup, id=group_id)
    group.members.add(request.user)
    return redirect('groups:workout_groups')

@login_required
def leave_group(request, group_id):
    group = get_object_or_404(WorkoutGroup, id=group_id)
    group.members.remove(request.user)
    return redirect('groups:workout_groups')

@login_required
def create_group(request):
    if request.method == 'POST':
        form = WorkoutGroupForm(request.POST)
        if form.is_valid():
            group = form.save()
            group.members.add(request.user)
            messages.success(request, 'Group created successfully!')
            return redirect('groups:group_detail', group_id=group.id)
    else:
        form = WorkoutGroupForm()
    return render(request, 'groups/create_group.html', {'form': form})

@login_required
def group_detail(request, group_id):
    group = get_object_or_404(WorkoutGroup, id=group_id)
    if request.user not in group.members.all():
        messages.error(request, 'You are not a member of this group.')
        return redirect('groups:workout_groups')
    challenges = group.challenges.all()
    return render(request, 'groups/group_detail.html', {
        'group': group,
        'challenges': challenges
    })

@login_required
def create_challenge(request, group_id):
    group = get_object_or_404(WorkoutGroup, id=group_id)
    if request.user not in group.members.all():
        messages.error(request, 'You are not a member of this group.')
        return redirect('groups:workout_groups')
    
    if request.method == 'POST':
        form = ChallengeForm(request.POST)
        if form.is_valid():
            challenge = form.save(commit=False)
            challenge.group = group
            challenge.save()
            challenge.participants.add(request.user)
            messages.success(request, 'Challenge created successfully!')
            return redirect('groups:group_detail', group_id=group.id)
    else:
        form = ChallengeForm()
    
    return render(request, 'groups/create_challenge.html', {
        'form': form,
        'group': group
    })

@login_required
def join_challenge(request, group_id, challenge_id):
    group = get_object_or_404(WorkoutGroup, id=group_id)
    challenge = get_object_or_404(Challenge, id=challenge_id, group=group)
    
    if request.user in group.members.all():
        challenge.participants.add(request.user)
        messages.success(request, f'You have joined the challenge: {challenge.title}')
    else:
        messages.error(request, 'You must be a member of the group to join its challenges.')
    
    return redirect('groups:group_detail', group_id=group_id)

@login_required
def leave_challenge(request, group_id, challenge_id):
    group = get_object_or_404(WorkoutGroup, id=group_id)
    challenge = get_object_or_404(Challenge, id=challenge_id, group=group)
    challenge.participants.remove(request.user)
    messages.success(request, f'You have left the challenge: {challenge.title}')
    return redirect('groups:group_detail', group_id=group_id)

@login_required
def complete_challenge(request, group_id, challenge_id):
    group = get_object_or_404(WorkoutGroup, id=group_id)
    challenge = get_object_or_404(Challenge, id=challenge_id, group=group)
    
    if request.user in group.members.all():
        if not challenge.completed:  # Only increment counters if challenge wasn't already completed
            challenge.completed = True
            challenge.save()
            
            # Increment completed_challenges counter for all participants
            for participant in challenge.participants.all():
                participant.profile.completed_challenges += 1
                participant.profile.save()
            
            messages.success(request, f'Challenge marked as complete: {challenge.title}')
        else:
            messages.info(request, 'This challenge was already completed.')
    else:
        messages.error(request, 'You must be a member of the group to complete challenges.')
    
    return redirect('groups:group_detail', group_id=group_id)