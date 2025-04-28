
# Create your views here.
from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from .models import WorkoutGroup
from .forms import WorkoutGroupForm


def workout_groups(request):
    groups = WorkoutGroup.objects.all()
    return render(request, 'groups/workout_groups.html', {'groups': groups})

@login_required
def join_group(request, group_id):
    group = get_object_or_404(WorkoutGroup, id=group_id)
    group.members.add(request.user)
    return redirect('groups:workout_groups_list')

@login_required
def leave_group(request, group_id):
    group = get_object_or_404(WorkoutGroup, id=group_id)
    group.members.remove(request.user)
    return redirect('groups:workout_groups_list')

@login_required
def workout_groups_view(request):
    groups = WorkoutGroup.objects.all()

    # Groups the user is in
    user_groups = groups.filter(members=request.user)

    # Groups the user is not in (groups they can join)
    available_groups = groups.exclude(members=request.user)

    return render(request, 'groups/workout_groups.html', {
        'workout_groups_list': groups,
        'user_groups': user_groups,
        'available_groups': available_groups,
    })


def create_group(request):
    if request.method == 'POST':
        form = WorkoutGroupForm(request.POST)
        if form.is_valid():
            # Save the new group
            new_group = form.save(commit=False)
            new_group.save()

            # Add the current user to the group
            new_group.members.add(request.user)

            return redirect('groups:workout_groups_list')  # Redirect back to the workout groups page
    else:
        form = WorkoutGroupForm()

    return render(request, 'groups/create_group.html', {'form': form})