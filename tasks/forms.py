from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User
from django.utils.translation import gettext_lazy as _
from .models import Task, UserProfile

class ProfileUpdateForm(forms.ModelForm):
    class Meta:
        model = UserProfile
        fields = ['bio', 'avatar', 'phone_number', 'position']
        widgets = {
            'bio': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
            'avatar': forms.FileInput(attrs={'class': 'form-control'}),
            'phone_number': forms.TextInput(attrs={'class': 'form-control'}),
            'position': forms.TextInput(attrs={'class': 'form-control'})
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['bio'].help_text = _('Tell us about yourself')
        self.fields['phone_number'].help_text = _('Enter your contact number')
        self.fields['position'].help_text = _('Your role or position in the organization')

class TaskForm(forms.ModelForm):
    class Meta:
        model = Task
        fields = ['title', 'description', 'due_date', 'priority', 'task_type', 'assigned_to']
        widgets = {
            'title': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': _('Enter task title'),
                'required': True,
                'minlength': '3'
            }),
            'description': forms.Textarea(attrs={
                'class': 'form-control',
                'placeholder': _('Enter task description'),
                'rows': 4
            }),
            'due_date': forms.DateTimeInput(attrs={
                'class': 'form-control',
                'type': 'datetime-local',
                'required': True
            }),
            'priority': forms.Select(attrs={'class': 'form-select', 'required': True}),
            'task_type': forms.Select(attrs={'class': 'form-select', 'required': True}),
            'assigned_to': forms.Select(attrs={'class': 'form-select', 'required': True})
        }

    def __init__(self, *args, **kwargs):
        user = kwargs.pop('user', None)
        super().__init__(*args, **kwargs)
        
        try:
            # Filter assigned_to queryset based on user role
            if user and user.profile.role == UserProfile.Role.ADMINISTRATOR:
                self.fields['assigned_to'].queryset = User.objects.filter(is_active=True)
            else:
                self.fields['assigned_to'].queryset = User.objects.filter(
                    is_active=True,
                    profile__role=UserProfile.Role.COWORKER
                )
        except UserProfile.DoesNotExist:
            self.fields['assigned_to'].queryset = User.objects.none()
        
        # Add help texts
        self.fields['title'].help_text = _('Minimum 3 characters')
        self.fields['due_date'].help_text = _('When this task needs to be completed')
        self.fields['priority'].help_text = _('Task priority level')
        self.fields['task_type'].help_text = _('Type of task')
        self.fields['assigned_to'].help_text = _('Team member responsible for this task')

    def clean_due_date(self):
        due_date = self.cleaned_data.get('due_date')
        if not due_date:
            raise forms.ValidationError(_('Due date is required'))
        return due_date

    def clean_title(self):
        title = self.cleaned_data.get('title')
        if len(title) < 3:
            raise forms.ValidationError(_('Title must be at least 3 characters long'))
        return title

    def clean_assigned_to(self):
        assigned_to = self.cleaned_data.get('assigned_to')
        if not assigned_to:
            raise forms.ValidationError(_('Please select a team member'))
        try:
            if not assigned_to.profile:
                raise forms.ValidationError(_('Selected user has no profile'))
        except UserProfile.DoesNotExist:
            raise forms.ValidationError(_('Selected user has no profile'))
        return assigned_to

    def clean_priority(self):
        priority = self.cleaned_data.get('priority')
        if not priority:
            raise forms.ValidationError(_('Priority is required'))
        return priority

    def clean_task_type(self):
        task_type = self.cleaned_data.get('task_type')
        if not task_type:
            raise forms.ValidationError(_('Task type is required'))
        return task_type

    def clean_description(self):
        description = self.cleaned_data.get('description')
        if description and len(description) < 10:
            raise forms.ValidationError(_('Description must be at least 10 characters long'))
        return description

    def clean(self):
        cleaned_data = super().clean()
        title = cleaned_data.get('title')
        description = cleaned_data.get('description')
        
        if title and description and title == description:
            raise forms.ValidationError(_('Title and description cannot be the same'))
        
        return cleaned_data

class UserRegistrationForm(UserCreationForm):
    email = forms.EmailField(
        required=True,
        widget=forms.EmailInput(attrs={
            'class': 'form-control',
            'placeholder': _('Enter your email')
        })
    )
    
    class Meta:
        model = User
        fields = ('username', 'email', 'password1', 'password2')
        widgets = {
            'username': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': _('Choose a username')
            }),
            'password1': forms.PasswordInput(attrs={
                'class': 'form-control',
                'placeholder': _('Enter your password')
            }),
            'password2': forms.PasswordInput(attrs={
                'class': 'form-control',
                'placeholder': _('Confirm your password')
            })
        }
    
    def clean_email(self):
        email = self.cleaned_data.get('email')
        if User.objects.filter(email=email).exists():
            raise forms.ValidationError(_('This email is already registered'))
        return email
    
    def clean_username(self):
        username = self.cleaned_data.get('username')
        if User.objects.filter(username=username).exists():
            raise forms.ValidationError(_('This username is already taken'))
        return username
    
    def clean_password2(self):
        password1 = self.cleaned_data.get('password1')
        password2 = self.cleaned_data.get('password2')
        if password1 and password2 and password1 != password2:
            raise forms.ValidationError(_('Passwords do not match'))
        return password2
    
    def clean_password1(self):
        password1 = self.cleaned_data.get('password1')
        if len(password1) < 8:
            raise forms.ValidationError(_('Password must be at least 8 characters long'))
        return password1
    
    def save(self, commit=True):
        user = super().save(commit=False)
        user.email = self.cleaned_data['email']
        if commit:
            user.save()
            UserProfile.objects.create(user=user)
        return user
