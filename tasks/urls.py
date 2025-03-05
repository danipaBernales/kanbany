from django.urls import path
from . import views
from django.contrib.auth import views as auth_views

app_name = 'tasks'

urlpatterns = [
    # Public URLs
    path('', views.index, name='index'),
    path('register/', views.register, name='register'),
    path('login/', auth_views.LoginView.as_view(template_name='tasks/login.html'), name='login'),
    path('logout/', auth_views.LogoutView.as_view(next_page='tasks:index'), name='logout'),
    
    # Protected URLs
    path('dashboard/', views.dashboard, name='dashboard'),
    path('tasks/', views.task_list, name='task_list'),
]
