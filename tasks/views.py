from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from .forms import UserRegistrationForm
from django.contrib import messages
from .models import Task

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
    return render(request, 'tasks/dashboard.html')

@login_required
def task_list(request):
    todo_tasks = Task.objects.filter(status='TODO', assigned_to=request.user)
    in_progress_tasks = Task.objects.filter(status='IN_PROGRESS', assigned_to=request.user)
    review_tasks = Task.objects.filter(status='REVIEW', assigned_to=request.user)
    
    context = {
        'todo_tasks': todo_tasks,
        'in_progress_tasks': in_progress_tasks,
        'review_tasks': review_tasks,
    }
    return render(request, 'tasks/task_list.html', context)
    
