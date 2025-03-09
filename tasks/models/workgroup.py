from django.db import models
from django.contrib.auth.models import User
from django.core.exceptions import ValidationError
from .organization import Organization, OrganizationMember

class WorkGroup(models.Model):
    name = models.CharField(max_length=100)
    description = models.TextField(blank=True)
    organization = models.ForeignKey(Organization, on_delete=models.CASCADE, related_name='workgroups')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    is_active = models.BooleanField(default=True)
    max_members = models.PositiveIntegerField(default=10)
    color_tag = models.CharField(max_length=7, default='#0d6efd')

    class Meta:
        ordering = ['-created_at']
        unique_together = ['name', 'organization']

    def __str__(self):
        return f'{self.name} ({self.organization.name})'

    def clean(self):
        # Ensure the creator is a member of the organization
        if not OrganizationMember.objects.filter(
            organization=self.organization,
            user=self.created_by,
            role__in=['OWNER', 'ADMIN']
        ).exists():
            raise ValidationError('Only organization owners and admins can create work groups')

class WorkGroupMember(models.Model):
    ROLE_CHOICES = [
        ('ADMIN', 'Group Admin'),
        ('MEMBER', 'Group Member')
    ]

    workgroup = models.ForeignKey(WorkGroup, on_delete=models.CASCADE, related_name='members')
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='workgroup_memberships')
    role = models.CharField(max_length=20, choices=ROLE_CHOICES, default='MEMBER')
    joined_at = models.DateTimeField(auto_now_add=True)
    invited_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, related_name='sent_group_invitations')
    is_active = models.BooleanField(default=True)

    class Meta:
        unique_together = ['workgroup', 'user']
        ordering = ['workgroup', '-joined_at']

    def __str__(self):
        return f'{self.user.username} - {self.workgroup.name} ({self.role})'

    def clean(self):
        # Ensure the user is a member of the organization
        if not OrganizationMember.objects.filter(
            organization=self.workgroup.organization,
            user=self.user
        ).exists():
            raise ValidationError('User must be a member of the organization to join a work group')

class WorkGroupInvitation(models.Model):
    STATUS_CHOICES = [
        ('PENDING', 'Pending'),
        ('ACCEPTED', 'Accepted'),
        ('REJECTED', 'Rejected'),
        ('EXPIRED', 'Expired')
    ]

    workgroup = models.ForeignKey(WorkGroup, on_delete=models.CASCADE, related_name='invitations')
    email = models.EmailField()
    invited_by = models.ForeignKey(User, on_delete=models.CASCADE, related_name='group_invitations_sent')
    role = models.CharField(max_length=20, choices=WorkGroupMember.ROLE_CHOICES, default='MEMBER')
    created_at = models.DateTimeField(auto_now_add=True)
    expires_at = models.DateTimeField()
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='PENDING')
    invitation_token = models.CharField(max_length=100, unique=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f'Invitation to {self.workgroup.name} for {self.email}'

    def clean(self):
        # Ensure the inviter has permission to invite
        if not WorkGroupMember.objects.filter(
            workgroup=self.workgroup,
            user=self.invited_by,
            role='ADMIN'
        ).exists():
            raise ValidationError('Only group admins can send invitations')