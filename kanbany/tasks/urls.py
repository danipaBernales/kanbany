from django.urls import path
from django.contrib.auth import views as auth_views
from django.utils.translation import gettext_lazy as _
from . import views

app_name = 'tasks'

urlpatterns = [
    # Public URLs
    path('', views.index, name='index'),
    
    # Authentication URLs
    path('login/', auth_views.LoginView.as_view(
        template_name='tasks/login.html',
        redirect_authenticated_user=True,
        next_page='tasks:dashboard',
        extra_context={'title': _('Login')}
    ), name='login'),
    path('logout/', views.custom_logout, name='logout'),
    path('register/', views.register, name='register'),
    
    # Password Reset URLs
    path('password-reset/', auth_views.PasswordResetView.as_view(
        template_name='tasks/password_reset.html',
        email_template_name='tasks/password_reset_email.html',
        subject_template_name='tasks/password_reset_subject.txt',
        success_url='/password-reset/done/'
    ), name='password_reset'),
    path('password-reset/done/', auth_views.PasswordResetDoneView.as_view(
        template_name='tasks/password_reset_done.html'
    ), name='password_reset_done'),
    path('reset/<uidb64>/<token>/', auth_views.PasswordResetConfirmView.as_view(
        template_name='tasks/password_reset_confirm.html',
        success_url='/reset/done/'
    ), name='password_reset_confirm'),
    path('reset/done/', auth_views.PasswordResetCompleteView.as_view(
        template_name='tasks/password_reset_complete.html'
    ), name='password_reset_complete'),
    
    # Protected URLs
    path('dashboard/', views.dashboard, name='dashboard'),
    path('profile/', views.profile_view, name='profile'),
    path('profile/update/', views.update_profile, name='update_profile'),
    
    # Task Management URLs
    path('task/create/', views.TaskCreateView.as_view(), name='task_create'),
    path('task/<int:pk>/edit/', views.TaskUpdateView.as_view(), name='task_edit'),
    path('task/<int:pk>/status/', views.update_task_status, name='update_task_status'),
    path('task/<int:pk>/delete/', views.delete_task, name='delete_task'),
    path('task/<int:pk>/', views.task_detail, name='task_detail'),
    path('tasks/my/', views.my_tasks, name='my_tasks'),
    path('tasks/team/', views.team_tasks, name='team_tasks'),
]
