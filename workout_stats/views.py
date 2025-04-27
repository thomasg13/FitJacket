from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from datetime import datetime, timedelta
from django.db.models import Sum
from workouts.models import Workout, TimedExercise
from goals.models import FitnessGoal
from decimal import Decimal



@login_required
def statistics(request):
    # Get user's goals
    try:
        goal = FitnessGoal.objects.get(user=request.user)
    except FitnessGoal.DoesNotExist:
        goal = None

    # Calculate this week's progress
    today = datetime.now().date()
    week_start = today - timedelta(days=today.weekday())
    week_end = week_start + timedelta(days=6)
    
    # Get this week's workout days
    this_week_days = Workout.objects.filter(
        user=request.user,
        date__range=[week_start, week_end]
    ).values('date').distinct().count()
    
    # Get this week's miles
    this_week_miles = TimedExercise.objects.filter(
        workout__user=request.user,
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
            user=request.user,
            date__range=[week_start, week_end]
        ).values('date').distinct().count()
        workout_days.append(days_worked)
        
        miles = TimedExercise.objects.filter(
            workout__user=request.user,
            workout__date__range=[week_start, week_end],
            distance__isnull=False
        ).aggregate(total=Sum('distance'))['total'] or 0
        total_miles.append(float(miles))

    context = {
        'dates': dates,
        'workout_days': workout_days,
        'total_miles': total_miles,
        'goal': goal,
        'this_week_days': this_week_days,
        'this_week_miles': this_week_miles,
        'days_progress': days_progress,
        'miles_progress': miles_progress,
    }
    return render(request, 'workout_stats/statistics.html', context)
