from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.contrib import messages
from django.shortcuts import render, get_object_or_404, redirect

from challenge.models import Challenge
from goals.models import FitnessGoal
from groups.models import WorkoutGroup
from socials.models import FriendRequest
from workouts.models import Workout


# Create your views here.

@login_required
def home(request):
    pending_requests = FriendRequest.objects.filter(to_user=request.user, is_accepted=False)

    outgoing_requests = FriendRequest.objects.filter(from_user=request.user, is_accepted=False)

    sent = FriendRequest.objects.filter(from_user=request.user, is_accepted=True)
    received = FriendRequest.objects.filter(to_user=request.user, is_accepted=True)
    friends = [fr.to_user for fr in sent] + [fr.from_user for fr in received]

    return render(request, 'socials/socials.html', {
        'pending_requests': pending_requests,
        'outgoing_requests': outgoing_requests,
        'friends': friends,
    })


def search_users(request):
    query = request.GET.get('q')
    users = []

    if query:
        users = User.objects.filter(username__icontains=query)

    return render(request, 'socials/search_results.html', {'users': users, 'query': query})

@login_required
def send_friend_request(request, user_id):
    user = get_object_or_404(User, id=user_id)
    if user == request.user: # can't friend yourself
        messages.error(request, "You can't send a friend request to yourself!")
        return redirect('socials:home')
    FriendRequest.objects.get_or_create(from_user=request.user, to_user=user)
    return redirect('socials:home')

@login_required
def accept_friend_request(request, request_id):
    friend_request = get_object_or_404(FriendRequest, id=request_id)
    if friend_request.to_user == request.user:
        friend_request.is_accepted = True
        friend_request.save()
    return redirect('socials:home')

@login_required
def unfriend(request, user_id):
    if request.method == "POST":
        other_user = get_object_or_404(User, id=user_id)

        FriendRequest.objects.filter(
            from_user=request.user, to_user=other_user, is_accepted=True
        ).delete()
        FriendRequest.objects.filter(
            from_user=other_user, to_user=request.user, is_accepted=True
        ).delete()

        messages.success(request, f"You have unfriended {other_user.username}.")

    return redirect('socials:home')

@login_required
def cancel_friend_request(request, request_id):
    if request.method == "POST":
        friend_request = get_object_or_404(FriendRequest, id=request_id, from_user=request.user, is_accepted=False)
        friend_request.delete()
        messages.success(request, "Friend request canceled.")

    return redirect('socials:home')

@login_required
def reject_friend_request(request, request_id):
    if request.method == "POST":
        friend_request = get_object_or_404(FriendRequest, id=request_id, to_user=request.user, is_accepted=False)
        friend_request.delete()
        messages.success(request, "Friend request rejected.")

    return redirect('socials:home')

@login_required
def friend_profile(request, user_id):
    user = get_object_or_404(User, id=user_id)

    # Can only view if friend with the requested user, can't just change url to view users
    if user != request.user: # Allows user to view their own profile
        sent = FriendRequest.objects.filter(from_user=request.user, to_user=user, is_accepted=True)
        received = FriendRequest.objects.filter(from_user=user, to_user=request.user, is_accepted=True)
        if not sent.exists() and not received.exists():
            messages.error(request, "You are not friends with this user.")
            return redirect('socials:home')

    created_challenges = Challenge.objects.filter(creator=user)
    participated_challenges = Challenge.objects.filter(participants=user)
    fitness_goal = FitnessGoal.objects.filter(user=user).first()
    groups = WorkoutGroup.objects.filter(members=user)
    workouts = Workout.objects.filter(user=user).order_by('-date')[:5]  # Show last 5 workouts

    return render(request, 'socials/friend_profile.html', {
        'friend': user,
        'created_challenges': created_challenges,
        'participated_challenges': participated_challenges,
        'fitness_goal': fitness_goal,
        'groups': groups,
        'workouts': workouts,
    })

@login_required
def my_profile(request):
  return redirect('socials:friend_profile', user_id=request.user.id)
