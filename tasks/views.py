from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from .forms import UserRegistrationForm
from django.contrib import messages
from .models import Task, WorkerGroup, UserProfile
from django.db.models import Count
from django.utils import timezone
from django.contrib.auth.views import LoginView
from django.contrib.auth import login, authenticate
from django.urls import reverse_lazy

def index(request):
    return render(request, 'tasks/index.html')

def register(request):
    if request.method == 'POST':
        form = UserRegistrationForm(request.POST)
        if form.is_valid():
            try:
                user = form.save()
                UserProfile.objects.get_or_create(user=user)
                messages.success(request, 'Account created successfully! You can now login.')
                return redirect('tasks:login')
            except Exception as e:
                messages.error(request, 'An error occurred during registration. Please try again.')
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
    

class CustomLoginView(LoginView):
    template_name = 'tasks/login.html'
    redirect_authenticated_user = True
    success_url = reverse_lazy('tasks:dashboard')
    
    def form_valid(self, form):
        try:
            username = form.cleaned_data.get('username')
            user = authenticate(
                self.request,
                username=username,
                password=form.cleaned_data.get('password')
            )
            
            if user is None:
                messages.error(self.request, 'Invalid username or password.')
                return self.form_invalid(form)
            
            profile, created = UserProfile.objects.get_or_create(user=user)
            
            if not profile.is_active:
                messages.error(self.request, 'Your account is not active.')
                return self.form_invalid(form)
            
            login(self.request, user)
            messages.success(self.request, f'Welcome back, {username}!')
            return super().form_valid(form)
            
        except Exception as e:
            import logging
            logger = logging.getLogger(__name__)
            logger.error(f'Login error for user {username}: {str(e)}')
            messages.error(self.request, 'An error occurred during login. Please try again.')
            return self.form_invalid(form)
    
    def get_success_url(self):
        return str(self.success_url)
    
