from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.contrib import messages
from django.shortcuts import render, get_object_or_404, redirect

from socials.models import FriendRequest


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