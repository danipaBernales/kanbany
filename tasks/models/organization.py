from django.db import models
from django.contrib.auth.models import User
from django.core.exceptions import ValidationError

class Organization(models.Model):
    name = models.CharField(max_length=200)
    description = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    owner = models.ForeignKey(User, on_delete=models.PROTECT, related_name='owned_organizations')
    is_active = models.BooleanField(default=True)
    website = models.URLField(blank=True)
    logo = models.ImageField(upload_to='organization_logos/', null=True, blank=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return self.name

    def clean(self):
        if not self.owner.userprofile.role == 'ADMIN':
            raise ValidationError('Only administrators can create organizations')

class OrganizationMember(models.Model):
    ROLE_CHOICES = [
        ('OWNER', 'Organization Owner'),
        ('ADMIN', 'Organization Admin'),
        ('MEMBER', 'Organization Member')
    ]

    organization = models.ForeignKey(Organization, on_delete=models.CASCADE, related_name='members')
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='organization_memberships')
    role = models.CharField(max_length=20, choices=ROLE_CHOICES, default='MEMBER')
    joined_at = models.DateTimeField(auto_now_add=True)
    invited_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, related_name='sent_org_invitations')
    is_active = models.BooleanField(default=True)

    class Meta:
        unique_together = ['organization', 'user']
        ordering = ['organization', '-joined_at']

    def __str__(self):
        return f'{self.user.username} - {self.organization.name} ({self.role})'

class OrganizationInvitation(models.Model):
    STATUS_CHOICES = [
        ('PENDING', 'Pending'),
        ('ACCEPTED', 'Accepted'),
        ('REJECTED', 'Rejected'),
        ('EXPIRED', 'Expired')
    ]

    organization = models.ForeignKey(Organization, on_delete=models.CASCADE, related_name='invitations')
    email = models.EmailField()
    invited_by = models.ForeignKey(User, on_delete=models.CASCADE, related_name='org_invitations_sent')
    role = models.CharField(max_length=20, choices=OrganizationMember.ROLE_CHOICES, default='MEMBER')
    created_at = models.DateTimeField(auto_now_add=True)
    expires_at = models.DateTimeField()
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='PENDING')
    invitation_token = models.CharField(max_length=100, unique=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f'Invitation to {self.organization.name} for {self.email}'