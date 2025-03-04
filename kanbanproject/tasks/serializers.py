from rest_framework import serializers
from django.contrib.auth.models import User
from django.utils.translation import gettext_lazy as _
from .models import Task

class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['id', 'username', 'email']
        read_only_fields = ['id']

class TaskSerializer(serializers.HyperlinkedModelSerializer):
    user = UserSerializer(read_only=True)
    status_display = serializers.CharField(source='get_status_display', read_only=True)
    priority_display = serializers.CharField(source='get_priority_display', read_only=True)
    
    class Meta:
        model = Task
        fields = [
            'url', 'id', 'title', 'notes', 
            'status', 'status_display',
            'priority', 'priority_display',
            'created_at', 'last_edited',
            'user'
        ]
        read_only_fields = ['id', 'created_at', 'last_edited', 'user']
        
    def validate_title(self, value):
        """
        Check that the title is not too short or contains only whitespace
        """
        if len(value.strip()) < 3:
            raise serializers.ValidationError(
                _('Title must be at least 3 characters long (excluding whitespace)')
            )
        return value.strip()
    
    def validate(self, data):
        """
        Check that the status and priority are valid
        """
        if 'status' in data and data['status'] not in dict(Task.Status.choices):
            raise serializers.ValidationError({
                'status': _('Invalid status value')
            })
            
        if 'priority' in data and data['priority'] not in dict(Task.Priority.choices):
            raise serializers.ValidationError({
                'priority': _('Invalid priority value')
            })
            
        return data
