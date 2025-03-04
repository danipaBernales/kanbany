from django.contrib.auth.models import User
from django.db import models
from django.core.validators import MinLengthValidator
from django.utils.translation import gettext_lazy as _

class UserProfile(models.Model):
    class Role(models.TextChoices):
        ADMINISTRATOR = 'ADMINISTRATOR', _('Administrator')
        COWORKER = 'COWORKER', _('Coworker')
    
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='profile')
    role = models.CharField(
        max_length=20,
        choices=Role.choices,
        default=Role.COWORKER,
        help_text=_('User role in the system')
    )
    
    def __str__(self):
        return f"{self.user.username} - {self.get_role_display()}"

    class Meta:
        verbose_name = _('User Profile')
        verbose_name_plural = _('User Profiles')

class Task(models.Model):
    class Status(models.TextChoices):
        TODO = 'TODO', _('To Do')
        IN_PROGRESS = 'IN_PROGRESS', _('In Progress')
        REVIEW = 'REVIEW', _('In Review')
        APPROVED = 'APPROVED', _('Approved')
        REJECTED = 'REJECTED', _('Rejected')
    
    class Priority(models.TextChoices):
        LOW = 'LOW', _('Low')
        NORMAL = 'NORMAL', _('Normal')
        HIGH = 'HIGH', _('High')
        URGENT = 'URGENT', _('Urgent')
    
    class TaskType(models.TextChoices):
        FEATURE = 'FEATURE', _('Feature')
        BUG = 'BUG', _('Bug')
        IMPROVEMENT = 'IMPROVEMENT', _('Improvement')
        DOCUMENTATION = 'DOCUMENTATION', _('Documentation')
        OTHER = 'OTHER', _('Other')
    
    title = models.CharField(
        max_length=200,
        validators=[MinLengthValidator(3)],
        help_text=_('Task title (minimum 3 characters)')
    )
    description = models.TextField(
        max_length=1000,
        blank=True,
        help_text=_('Detailed description of the task')
    )
    status = models.CharField(
        max_length=20,
        choices=Status.choices,
        default=Status.TODO,
        help_text=_('Current status of the task')
    )
    priority = models.CharField(
        max_length=20,
        choices=Priority.choices,
        default=Priority.NORMAL,
        help_text=_('Task priority level')
    )
    task_type = models.CharField(
        max_length=20,
        choices=TaskType.choices,
        default=TaskType.OTHER,
        help_text=_('Type of task')
    )
    due_date = models.DateTimeField(
        null=True,
        blank=True,
        help_text=_('When this task is due')
    )
    created_at = models.DateTimeField(
        auto_now_add=True,
        help_text=_('When the task was created')
    )
    last_edited = models.DateTimeField(
        auto_now=True,
        help_text=_('When the task was last modified')
    )
    created_by = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='created_tasks',
        help_text=_('Administrator who created this task')
    )
    assigned_to = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='assigned_tasks',
        help_text=_('Coworker assigned to this task')
    )
    review_notes = models.TextField(
        max_length=500,
        blank=True,
        help_text=_('Notes from the review process')
    )

    def __str__(self):
        return f"{self.title} ({self.get_status_display()})"

    class Meta:
        ordering = ['-priority', 'due_date', 'created_at']
        verbose_name = _('Task')
        verbose_name_plural = _('Tasks')

    def can_transition_to(self, new_status):
        """Check if the task can transition to the new status."""
        valid_transitions = {
            self.Status.TODO: [self.Status.IN_PROGRESS],
            self.Status.IN_PROGRESS: [self.Status.REVIEW],
            self.Status.REVIEW: [self.Status.APPROVED, self.Status.REJECTED],
            self.Status.REJECTED: [self.Status.IN_PROGRESS],
            self.Status.APPROVED: []
        }
        return new_status in valid_transitions.get(self.status, [])

    def save(self, *args, **kwargs):
        self.full_clean()
        super().save(*args, **kwargs)

    def get_priority_class(self):
        return {
            self.Priority.URGENT: 'task-urgent',
            self.Priority.HIGH: 'task-high',
            self.Priority.NORMAL: 'task-normal',
            self.Priority.LOW: 'task-low'
        }.get(self.priority, 'task-normal')
