from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from datetime import datetime, timedelta
from django.db.models import Sum
from workouts.models import Workout, TimedExercise

# Create your views here.

@login_required
def statistics(request):
    # Generate dates for the last 14 weeks
    today = datetime.now().date()
    dates = []
    week_starts = []
    for i in range(14):
        week_start = today - timedelta(days=today.weekday() + (i * 7))
        week_end = week_start + timedelta(days=6)
        dates.append(f"{week_start.strftime('%b %d')}-{week_end.strftime('%d')}")
        week_starts.append(week_start)
    dates.reverse()  # Show oldest to newest
    week_starts.reverse()

    # Calculate workout days and miles for each week
    workout_days = []
    total_miles = []
    
    for week_start in week_starts:
        week_end = week_start + timedelta(days=6)
        
        # Get unique workout days in this week
        days_worked = Workout.objects.filter(
            user=request.user,
            date__range=[week_start, week_end]
        ).values('date').distinct().count()
        workout_days.append(days_worked)
        
        # Get total miles for this week
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
    }
    return render(request, 'workout_stats/statistics.html', context)
