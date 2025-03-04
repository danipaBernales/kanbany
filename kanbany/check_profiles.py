import os
import django
import sys
from pathlib import Path

# Add the project directory to the Python path
sys.path.append(str(Path(__file__).resolve().parent))

# Set up Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'kanbany.settings')
django.setup()

from django.contrib.auth.models import User
from tasks.models import UserProfile

def check_and_fix_profiles():
    # Get all users
    users = User.objects.all()
    
    for user in users:
        try:
            profile = user.profile
            print(f"User {user.username} has profile with role: {profile.role}")
        except UserProfile.DoesNotExist:
            # Create profile if it doesn't exist
            if user.is_superuser:
                role = UserProfile.Role.ADMINISTRATOR
            else:
                role = UserProfile.Role.COWORKER
            UserProfile.objects.create(user=user, role=role)
            print(f"Created profile for user {user.username} with role: {role}")

if __name__ == '__main__':
    check_and_fix_profiles() 