from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from .forms import UserRegistrationForm
from django.contrib import messages
from .models import Task, WorkerGroup, UserProfile
from django.db.models import Count
from django.utils import timezone

def index(request):
    return render(request, 'tasks/index.html')

def register(request):
    if request.method == 'POST':
        form = UserRegistrationForm(request.POST)
        if form.is_valid():
            user = form.save()
            messages.success(request, 'Account created successfully! You can now login.')
            return redirect('tasks:login')
    else:
        form = UserRegistrationForm()
    return render(request, 'tasks/register.html', {'form': form})

@login_required
def dashboard(request):
    user_profile = request.user.userprofile
    context = {}

    if user_profile.role in ['ADMIN', 'LEADER']:
        # Admin and Leader specific data
        if user_profile.role == 'ADMIN':
            groups = WorkerGroup.objects.all()
            all_users = User.objects.all()
        else:
            groups = WorkerGroup.objects.filter(leader=request.user)
            all_users = User.objects.filter(member_groups__in=groups).distinct()

        # Group statistics
        group_stats = groups.annotate(
            total_tasks=Count('tasks'),
            active_members=Count('members', filter=models.Q(members__userprofile__is_active=True))
        )

        context.update({
            'groups': groups,
            'group_stats': group_stats,
            'all_users': all_users,
            'total_users': all_users.count(),
            'active_users': all_users.filter(userprofile__is_active=True).count()
        })

    # Common dashboard data
    user_tasks = Task.objects.filter(assigned_to=request.user)
    context.update({
        'total_tasks': user_tasks.count(),
        'completed_tasks': user_tasks.filter(status='DONE').count(),
        'in_progress_tasks': user_tasks.filter(status='IN_PROGRESS').count(),
        'overdue_tasks': user_tasks.filter(due_date__lt=timezone.now()).exclude(status='DONE').count(),
        'my_tasks': user_tasks.order_by('-created_at')[:5],
        'user_role': user_profile.role
    })

    return render(request, 'tasks/dashboard.html', context)

@login_required
def task_list(request):
    user_profile = request.user.userprofile
    
    if user_profile.role in ['ADMIN', 'LEADER']:
        if user_profile.role == 'ADMIN':
            tasks = Task.objects.all()
        else:
            groups = WorkerGroup.objects.filter(leader=request.user)
            tasks = Task.objects.filter(group__in=groups)
    else:
        tasks = Task.objects.filter(assigned_to=request.user)

    context = {
        'todo_tasks': tasks.filter(status='TODO'),
        'in_progress_tasks': tasks.filter(status='IN_PROGRESS'),
        'review_tasks': tasks.filter(status='REVIEW'),
    }
    return render(request, 'tasks/task_list.html', context)
    
