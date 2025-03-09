from django.db import models
from django.contrib.auth.models import User
from django.core.mail import send_mail
from django.conf import settings
from django.template.loader import render_to_string
from django.contrib.sites.shortcuts import get_current_site
from django.urls import reverse
from django.db.models.signals import post_save
from django.dispatch import receiver

class Organization(models.Model):
    name = models.CharField(max_length=200)
    description = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    is_active = models.BooleanField(default=True)
    domain = models.CharField(max_length=100, blank=True, help_text='Organization email domain')

    def __str__(self):
        return self.name

class UserProfile(models.Model):
    ROLE_CHOICES = [
        ('MEMBER', 'Team Member'),
        ('LEADER', 'Team Leader'),
        ('ADMIN', 'Administrator')
    ]

    user = models.OneToOneField(User, on_delete=models.CASCADE)
    organization = models.ForeignKey(Organization, on_delete=models.CASCADE, related_name='members', null=True)
    bio = models.TextField(max_length=500, blank=True)
    avatar = models.ImageField(upload_to='avatars/', null=True, blank=True)
    phone_number = models.CharField(max_length=15, blank=True)
    position = models.CharField(max_length=100, blank=True)
    role = models.CharField(max_length=20, choices=ROLE_CHOICES, default='MEMBER')
    department = models.CharField(max_length=100, blank=True)
    is_active = models.BooleanField(default=True)
    corporate_email = models.EmailField(blank=True, help_text='Organization email address')
    job_title = models.CharField(max_length=100, blank=True)
    date_joined_org = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.user.username}'s Profile"

@receiver(post_save, sender=User)
def create_user_profile(sender, instance, created, **kwargs):
    if created:
        UserProfile.objects.create(user=instance)

@receiver(post_save, sender=User)
def save_user_profile(sender, instance, **kwargs):
    instance.userprofile.save()


class WorkerGroup(models.Model):
    name = models.CharField(max_length=100)
    description = models.TextField(blank=True)
    organization = models.ForeignKey(Organization, on_delete=models.CASCADE, related_name='groups')
    leader = models.ForeignKey(User, on_delete=models.CASCADE, related_name='led_groups')
    members = models.ManyToManyField(User, related_name='member_groups')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    is_active = models.BooleanField(default=True)
    max_members = models.PositiveIntegerField(default=10)
    color_tag = models.CharField(max_length=7, default='#0d6efd')
    parent_group = models.ForeignKey('self', null=True, blank=True, on_delete=models.SET_NULL, related_name='subgroups')
    group_type = models.CharField(max_length=50, default='team', help_text='Type of group (e.g., team, department, division)')
    access_level = models.IntegerField(default=0, help_text='Hierarchical access level within the organization')

    class Meta:
        ordering = ['-created_at']

    def get_active_members(self):
        return self.members.filter(userprofile__is_active=True)

    def __str__(self):
        return self.name

class Task(models.Model):
    STATUS_CHOICES = [
        ('TODO', 'To Do'),
        ('IN_PROGRESS', 'In Progress'),
        ('DONE', 'Done'),
        ('REVIEW', 'Under Review')
    ]

    PRIORITY_CHOICES = [
        ('HIGH', 'High'),
        ('MEDIUM', 'Medium'),
        ('LOW', 'Low')
    ]

    TASK_TYPE_CHOICES = [
        ('FEATURE', 'Feature'),
        ('BUG', 'Bug'),
        ('IMPROVEMENT', 'Improvement'),
        ('DOCUMENTATION', 'Documentation'),
        ('OTHER', 'Other')
    ]

    title = models.CharField(max_length=200)
    description = models.TextField()
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='TODO')
    priority = models.CharField(max_length=10, choices=PRIORITY_CHOICES, default='MEDIUM')
    task_type = models.CharField(max_length=15, choices=TASK_TYPE_CHOICES, default='OTHER')
    assigned_to = models.ForeignKey(User, on_delete=models.CASCADE, related_name='assigned_tasks')
    created_by = models.ForeignKey(User, on_delete=models.CASCADE, related_name='created_tasks')
    workgroup = models.ForeignKey(WorkerGroup, on_delete=models.CASCADE, related_name='tasks')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    due_date = models.DateTimeField(null=True, blank=True)
    estimated_hours = models.DecimalField(max_digits=5, decimal_places=2, null=True, blank=True)
    actual_hours = models.DecimalField(max_digits=5, decimal_places=2, null=True, blank=True)
    tags = models.CharField(max_length=200, blank=True, help_text='Comma-separated tags')
    parent_task = models.ForeignKey('self', null=True, blank=True, on_delete=models.SET_NULL, related_name='subtasks')
    order = models.PositiveIntegerField(default=0, help_text='Order within the same status')
    watchers = models.ManyToManyField(User, related_name='watched_tasks', blank=True)

    def __str__(self):
        return self.title

    def save(self, *args, **kwargs):
        is_new = self.pk is None
        old_status = None if is_new else Task.objects.get(pk=self.pk).status
        
        super().save(*args, **kwargs)

        if is_new:
            # Send email notification when task is created
            context = {
                'task': self,
                'site_url': settings.SITE_URL
            }
            html_message = render_to_string('tasks/emails/task_assigned.html', context)
            subject = f'New Task Assigned: {self.title}'
            send_mail(
                subject,
                '',
                settings.DEFAULT_FROM_EMAIL,
                [self.assigned_to.email],
                fail_silently=False,
                html_message=html_message
            )
        elif old_status != 'REVIEW' and self.status == 'REVIEW':
            # Send email notification when task is marked for review
            context = {
                'task': self,
                'site_url': settings.SITE_URL
            }
            html_message = render_to_string('tasks/emails/task_review.html', context)
            subject = f'Task Ready for Review: {self.title}'
            send_mail(
                subject,
                '',
                settings.DEFAULT_FROM_EMAIL,
                [self.group.admin.email],
                fail_silently=False,
                html_message=html_message
            )
