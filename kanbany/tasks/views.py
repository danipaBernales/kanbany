from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.contrib import messages
from django.urls import reverse_lazy, reverse
from django.views.generic.edit import CreateView, UpdateView
from django.contrib.auth import logout
from django.http import HttpResponseRedirect, Http404
from rest_framework import viewsets, permissions
from django.utils.translation import gettext_lazy as _
from .models import Task, UserProfile
from .forms import TaskForm, UserRegistrationForm, ProfileUpdateForm
from .serializers import TaskSerializer

def is_administrator(user):
    return user.is_authenticated and user.profile.role == UserProfile.Role.ADMINISTRATOR

def index(request):
    if request.user.is_authenticated:
        return redirect('tasks:dashboard')
    return render(request, 'tasks/index.html')

def register(request):
    if request.user.is_authenticated:
        return redirect('tasks:dashboard')
        
    if request.method == 'POST':
        form = UserRegistrationForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, _('Account created successfully. Please log in.'))
            return redirect('tasks:login')
        else:
            messages.error(request, _('Please correct the errors below.'))
    else:
        form = UserRegistrationForm()
    return render(request, 'tasks/register.html', {'form': form})

@login_required(login_url='tasks:login')
def dashboard(request):
    try:
        user_profile = request.user.profile
        tasks = Task.objects.all() if user_profile.role == UserProfile.Role.ADMINISTRATOR else Task.objects.filter(assigned_to=request.user)
        return render(request, 'tasks/dashboard.html', {
            'tasks': tasks,
            'is_admin': user_profile.role == UserProfile.Role.ADMINISTRATOR
        })
    except UserProfile.DoesNotExist:
        messages.error(request, _('User profile not found. Please contact support.'))
        return redirect('tasks:index')

@login_required(login_url='tasks:login')
def profile_view(request):
    try:
        return render(request, 'tasks/profile.html')
    except Exception as e:
        messages.error(request, _('Error loading profile. Please try again.'))
        return redirect('tasks:dashboard')

def custom_logout(request):
    logout(request)
    messages.success(request, _('You have been successfully logged out.'))
    return redirect('tasks:index')

class TaskCreateView(LoginRequiredMixin, CreateView):
    model = Task
    form_class = TaskForm
    template_name = 'tasks/task_form.html'
    success_url = reverse_lazy('tasks:dashboard')
    login_url = 'tasks:login'

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs['user'] = self.request.user
        return kwargs

    def form_valid(self, form):
        form.instance.created_by = self.request.user
        response = super().form_valid(form)
        messages.success(self.request, _('Task created successfully!'))
        return response

    def form_invalid(self, form):
        for field, errors in form.errors.items():
            for error in errors:
                messages.error(self.request, f"{field}: {error}")
        return super().form_invalid(form)

class TaskUpdateView(LoginRequiredMixin, UserPassesTestMixin, UpdateView):
    model = Task
    form_class = TaskForm
    template_name = 'tasks/task_form.html'
    success_url = reverse_lazy('tasks:dashboard')
    login_url = 'tasks:login'

    def test_func(self):
        try:
            task = self.get_object()
            return (self.request.user.profile.role == UserProfile.Role.ADMINISTRATOR or 
                    task.assigned_to == self.request.user)
        except (Task.DoesNotExist, UserProfile.DoesNotExist):
            return False

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs['user'] = self.request.user
        return kwargs

    def form_valid(self, form):
        try:
            response = super().form_valid(form)
            messages.success(self.request, _('Task updated successfully!'))
            return response
        except Exception as e:
            messages.error(self.request, _('Error updating task. Please try again.'))
            return self.form_invalid(form)

    def form_invalid(self, form):
        for field, errors in form.errors.items():
            for error in errors:
                messages.error(self.request, f"{field}: {error}")
        return super().form_invalid(form)

@login_required(login_url='tasks:login')
def update_task_status(request, pk):
    try:
        task = get_object_or_404(Task, pk=pk)
        
        # Check permissions
        if not (request.user.profile.role == UserProfile.Role.ADMINISTRATOR or 
                task.assigned_to == request.user):
            messages.error(request, _('You do not have permission to update this task.'))
            return redirect('tasks:dashboard')
        
        new_status = request.POST.get('status')
        if new_status in dict(Task.Status.choices):
            task.status = new_status
            task.save()
            messages.success(request, _('Task status updated to %(status)s') % 
                            {'status': task.get_status_display()})
        else:
            messages.error(request, _('Invalid status'))
    except Exception as e:
        messages.error(request, _('Error updating task status. Please try again.'))
    
    return redirect('tasks:dashboard')

@login_required(login_url='tasks:login')
def delete_task(request, pk):
    try:
        task = get_object_or_404(Task, pk=pk)
        if not (request.user.profile.role == UserProfile.Role.ADMINISTRATOR or 
                task.assigned_to == request.user):
            messages.error(request, _('You do not have permission to delete this task.'))
            return redirect('tasks:dashboard')
        
        task.delete()
        messages.success(request, _('Task deleted successfully!'))
    except Exception as e:
        messages.error(request, _('Error deleting task. Please try again.'))
    
    return redirect('tasks:dashboard')

@login_required(login_url='tasks:login')
def task_detail(request, pk):
    try:
        task = get_object_or_404(Task, pk=pk)
        if not (request.user.profile.role == UserProfile.Role.ADMINISTRATOR or 
                task.assigned_to == request.user):
            messages.error(request, _('You do not have permission to view this task.'))
            return redirect('tasks:dashboard')
        
        return render(request, 'tasks/task_detail.html', {'task': task})
    except Exception as e:
        messages.error(request, _('Error loading task details. Please try again.'))
        return redirect('tasks:dashboard')

@login_required(login_url='tasks:login')
def my_tasks(request):
    try:
        tasks = Task.objects.filter(assigned_to=request.user)
        return render(request, 'tasks/my_tasks.html', {'tasks': tasks})
    except Exception as e:
        messages.error(request, _('Error loading your tasks. Please try again.'))
        return redirect('tasks:dashboard')

@login_required(login_url='tasks:login')
def team_tasks(request):
    try:
        if not request.user.profile.role == UserProfile.Role.ADMINISTRATOR:
            messages.error(request, _('You do not have permission to view team tasks.'))
            return redirect('tasks:dashboard')
        
        tasks = Task.objects.all()
        return render(request, 'tasks/team_tasks.html', {'tasks': tasks})
    except Exception as e:
        messages.error(request, _('Error loading team tasks. Please try again.'))
        return redirect('tasks:dashboard')

@login_required(login_url='tasks:login')
def update_profile(request):
    try:
        if request.method == 'POST':
            form = ProfileUpdateForm(request.POST, instance=request.user.profile)
            if form.is_valid():
                form.save()
                messages.success(request, _('Profile updated successfully!'))
                return redirect('tasks:profile')
            else:
                messages.error(request, _('Please correct the errors below.'))
        else:
            form = ProfileUpdateForm(instance=request.user.profile)
        return render(request, 'tasks/update_profile.html', {'form': form})
    except Exception as e:
        messages.error(request, _('Error updating profile. Please try again.'))
        return redirect('tasks:profile')

class TasksViewSet(viewsets.ModelViewSet):
    serializer_class = TaskSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def get_queryset(self):
        try:
            user_profile = self.request.user.profile
            return Task.objects.all() if user_profile.role == UserProfile.Role.ADMINISTRATOR else Task.objects.filter(assigned_to=self.request.user)
        except UserProfile.DoesNotExist:
            return Task.objects.none()
