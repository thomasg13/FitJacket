from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.contrib import messages
from django.shortcuts import render, get_object_or_404, redirect
from datetime import datetime, timedelta
from django.db.models import Sum, Count, Q

from groups.models import Challenge
from goals.models import FitnessGoal
from groups.models import WorkoutGroup
from socials.models import FriendRequest, UserAchievement
from workouts.models import Workout, TimedExercise
from users.models import UserProfile


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

    # Check if already friends
    sent = FriendRequest.objects.filter(from_user=request.user, to_user=user, is_accepted=True)
    received = FriendRequest.objects.filter(from_user=user, to_user=request.user, is_accepted=True)
    if sent.exists() or received.exists():
        messages.error(request, "You are already friends with this user.")
        return redirect('socials:home')

    # Check if a request already sent
    pending = FriendRequest.objects.filter(from_user=request.user, to_user=user, is_accepted=False)
    if pending.exists():
        messages.info(request, "Friend request already sent and pending.")
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
    check_achievements(request.user)
    user = get_object_or_404(User, id=user_id)

    # Can only view if friend with the requested user, can't just change url to view users
    if user != request.user: # Allows user to view their own profile
        sent = FriendRequest.objects.filter(from_user=request.user, to_user=user, is_accepted=True)
        received = FriendRequest.objects.filter(from_user=user, to_user=request.user, is_accepted=True)
        if not sent.exists() and not received.exists():
            messages.error(request, "You are not friends with this user.")
            return redirect('socials:home')

    # Get user's goals
    try:
        goal = FitnessGoal.objects.get(user=user)
    except FitnessGoal.DoesNotExist:
        goal = None

    # Calculate this week's progress
    today = datetime.now().date()
    week_start = today - timedelta(days=today.weekday())
    week_end = week_start + timedelta(days=6)
    
    # Get this week's workout days
    this_week_days = Workout.objects.filter(
        user=user,
        date__range=[week_start, week_end]
    ).values('date').distinct().count()
    
    # Get this week's miles
    this_week_miles = TimedExercise.objects.filter(
        workout__user=user,
        workout__date__range=[week_start, week_end],
        distance__isnull=False
    ).aggregate(total=Sum('distance'))['total'] or 0
    this_week_miles = float(this_week_miles)

    # Calculate progress percentages
    if goal:
        days_progress = min(round(float(this_week_days) / float(goal.weekly_workout_days_goal) * 100 if goal.weekly_workout_days_goal else 0), 100)
        miles_progress = min(round(float(this_week_miles) / float(goal.weekly_miles_goal) * 100 if goal.weekly_miles_goal else 0), 100)
    else:
        days_progress = 0
        miles_progress = 0

    # Generate dates for the last 14 weeks
    dates = []
    week_starts = []
    for i in range(14):
        week_start = today - timedelta(days=today.weekday() + (i * 7))
        week_end = week_start + timedelta(days=6)
        dates.append(f"{week_start.strftime('%b %d')}-{week_end.strftime('%d')}")
        week_starts.append(week_start)
    dates.reverse()
    week_starts.reverse()

    # Calculate workout days and miles for each week
    workout_days = []
    total_miles = []
    
    for week_start in week_starts:
        week_end = week_start + timedelta(days=6)
        
        days_worked = Workout.objects.filter(
            user=user,
            date__range=[week_start, week_end]
        ).values('date').distinct().count()
        workout_days.append(days_worked)
        
        miles = TimedExercise.objects.filter(
            workout__user=user,
            workout__date__range=[week_start, week_end],
            distance__isnull=False
        ).aggregate(total=Sum('distance'))['total'] or 0
        total_miles.append(float(miles))

    fitness_goal = FitnessGoal.objects.filter(user=user).first()
    groups = WorkoutGroup.objects.filter(members=user)
    workouts = Workout.objects.filter(user=user).order_by('-date')[:5]  # Show last 5 workouts
    user_achievements = UserAchievement.objects.filter(user=request.user).select_related('achievement')

    return render(request, 'socials/friend_profile.html', {
        'friend': user,
        'fitness_goal': fitness_goal,
        'groups': groups,
        'workouts': workouts,
        'goal': goal,
        'this_week_days': this_week_days,
        'this_week_miles': this_week_miles,
        'days_progress': days_progress,
        'miles_progress': miles_progress,
        'dates': dates,
        'workout_days': workout_days,
        'total_miles': total_miles,
        'user_achievements': user_achievements
    })

@login_required
def my_profile(request):
  return redirect('socials:friend_profile', user_id=request.user.id)

@login_required
def friend_progress(request, user_id):
    user = get_object_or_404(User, id=user_id)

    # Can only view if friend with the requested user
    if user != request.user: # Allows user to view their own profile
        sent = FriendRequest.objects.filter(from_user=request.user, to_user=user, is_accepted=True)
        received = FriendRequest.objects.filter(from_user=user, to_user=request.user, is_accepted=True)
        if not sent.exists() and not received.exists():
            messages.error(request, "You are not friends with this user.")
            return redirect('socials:home')

    # Get user's goals
    try:
        goal = FitnessGoal.objects.get(user=user)
    except FitnessGoal.DoesNotExist:
        goal = None

    # Calculate this week's progress
    today = datetime.now().date()
    week_start = today - timedelta(days=today.weekday())
    week_end = week_start + timedelta(days=6)
    
    # Get this week's workout days
    this_week_days = Workout.objects.filter(
        user=user,
        date__range=[week_start, week_end]
    ).values('date').distinct().count()
    
    # Get this week's miles
    this_week_miles = TimedExercise.objects.filter(
        workout__user=user,
        workout__date__range=[week_start, week_end],
        distance__isnull=False
    ).aggregate(total=Sum('distance'))['total'] or 0
    this_week_miles = float(this_week_miles)

    # Calculate progress percentages
    if goal:
        days_progress = min(round(float(this_week_days) / float(goal.weekly_workout_days_goal) * 100 if goal.weekly_workout_days_goal else 0), 100)
        miles_progress = min(round(float(this_week_miles) / float(goal.weekly_miles_goal) * 100 if goal.weekly_miles_goal else 0), 100)
    else:
        days_progress = 0
        miles_progress = 0

    # Generate dates for the last 14 weeks
    dates = []
    week_starts = []
    for i in range(14):
        week_start = today - timedelta(days=today.weekday() + (i * 7))
        week_end = week_start + timedelta(days=6)
        dates.append(f"{week_start.strftime('%b %d')}-{week_end.strftime('%d')}")
        week_starts.append(week_start)
    dates.reverse()
    week_starts.reverse()

    # Calculate workout days and miles for each week
    workout_days = []
    total_miles = []
    
    for week_start in week_starts:
        week_end = week_start + timedelta(days=6)
        
        days_worked = Workout.objects.filter(
            user=user,
            date__range=[week_start, week_end]
        ).values('date').distinct().count()
        workout_days.append(days_worked)
        
        miles = TimedExercise.objects.filter(
            workout__user=user,
            workout__date__range=[week_start, week_end],
            distance__isnull=False
        ).aggregate(total=Sum('distance'))['total'] or 0
        total_miles.append(float(miles))

    return render(request, 'socials/friend_progress.html', {
        'friend': user,
        'goal': goal,
        'this_week_days': this_week_days,
        'this_week_miles': this_week_miles,
        'days_progress': days_progress,
        'miles_progress': miles_progress,
        'dates': dates,
        'workout_days': workout_days,
        'total_miles': total_miles,
    })

@login_required
def leaderboard(request):
    # Get top 10 users by completed challenges
    challenge_leaders = UserProfile.objects.order_by('-completed_challenges')[:10].values_list('user', 'completed_challenges')
    challenge_leaders = [(User.objects.get(id=user_id), count) for user_id, count in challenge_leaders]

    return render(request, 'socials/leaderboard.html', {
        'challenge_leaders': challenge_leaders,
    })


def check_achievements(user):
    from socials.models import Achievement, UserAchievement, FriendRequest
    from workouts.models import Workout, TimedExercise
    from users.models import UserProfile
    from groups.models import WorkoutGroup

    workout_count = Workout.objects.filter(user=user).count()

    total_miles = TimedExercise.objects.filter(
        workout__user=user,
        distance__isnull=False
    ).aggregate(total=Sum('distance'))['total'] or 0
    total_miles = float(total_miles)

    user_profile = UserProfile.objects.get(user=user)
    completed_challenges = user_profile.completed_challenges

    friends_made = FriendRequest.objects.filter(
        (Q(from_user=user) | Q(to_user=user)),
        is_accepted=True
    ).count()

    groups_joined = WorkoutGroup.objects.filter(members=user).count()

    achievements_to_check = [
        #(criteria_code, name, description, condition)
        ('first_workout', 'First Workout', 'Completed your first workout!', workout_count >= 1),
        ('5_workouts', '5 Workouts', 'Completed 5 workouts!', workout_count >= 5),
        ('10_workouts', '10 Workouts', 'Completed 10 workouts!', workout_count >= 10),
        ('50_workouts', '50 Workouts', 'Completed 50 workouts!', workout_count >= 50),
        ('first_challenge', 'First Challenge', 'Completed your first challenge!', completed_challenges >= 1),
        ('5_challenges', '5 Challenges', 'Completed 5 challenges!', completed_challenges >= 5),
        ('first_mile', 'First Mile', 'Completed your first mile!', total_miles >= 1),
        ('10_miles', '10 Miles', 'Completed 10 miles!', total_miles >= 10),
        ('50_miles', '50 Miles', 'Completed 50 miles!', total_miles >= 50),
        ('100_miles', '100 Miles', 'Completed 100 miles!', total_miles >= 100),
        ('first_friend', 'First Friend', 'Made your first friend!', friends_made >= 1),
        ('5_friends', '5 Friends', 'Made 5 friends!', friends_made >= 5),
        ('first_group', 'First Group', 'Joined your first group!', groups_joined >= 1),
        ('5_groups', '5 Groups', 'Joined 5 workout groups!', groups_joined >= 5),
    ]

    for code, name, description, condition in achievements_to_check:
        if condition:
            achievement, _ = Achievement.objects.get_or_create(criteria_code=code, defaults={
                'name': name,
                'description': description,
            })
            UserAchievement.objects.get_or_create(user=user, achievement=achievement)
