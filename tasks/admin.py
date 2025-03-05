from django.contrib import admin
from django.utils.translation import gettext_lazy as _
from .models import Task, UserProfile

@admin.register(UserProfile)
class UserProfileAdmin(admin.ModelAdmin):
    list_display = ['user', 'position']
    list_filter = ['position']
    search_fields = ['user__username', 'user__email', 'bio', 'position']
    ordering = ['user__username']

@admin.register(Task)
class TaskAdmin(admin.ModelAdmin):
    list_display = [
        'title',
        'status',
        'priority',
        'task_type',
        'created_by',
        'assigned_to',
        'due_date',
        'updated_at'
    ]
    list_filter = [
        'status',
        'priority',
        'task_type',
        'created_at',
        'due_date'
    ]
    search_fields = [
        'title',
        'description',
        'created_by__username',
        'assigned_to__username'
    ]
    ordering = ['-priority', 'due_date', '-created_at']
    readonly_fields = ['created_at', 'updated_at']
    
    fieldsets = [
        (None, {
            'fields': ('title', 'description')
        }),
        (_('Task Details'), {
            'fields': ('status', 'priority', 'task_type', 'due_date')
        }),
        (_('Assignment'), {
            'fields': ('created_by', 'assigned_to')
        }),
        (_('Review'), {
            'fields': ('review_notes',)
        }),
        (_('Timestamps'), {
            'fields': ('created_at', 'last_edited'),
            'classes': ('collapse',)
        })
    ]

    def get_queryset(self, request):
        qs = super().get_queryset(request)
        if request.user.is_superuser:
            return qs
        try:
            if request.user.profile.role == UserProfile.Role.ADMINISTRATOR:
                return qs.filter(created_by=request.user)
            return qs.filter(assigned_to=request.user)
        except UserProfile.DoesNotExist:
            return qs.none()

    def formfield_for_foreignkey(self, db_field, request, **kwargs):
        if db_field.name == "assigned_to":
            kwargs["queryset"] = UserProfile.objects.filter(
                role=UserProfile.Role.COWORKER
            ).select_related('user').values_list('user', flat=True)
        return super().formfield_for_foreignkey(db_field, request, **kwargs)
