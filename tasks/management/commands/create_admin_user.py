from django.core.management.base import BaseCommand
from django.contrib.auth.models import User
from django.db import transaction
from tasks.models import UserProfile

class Command(BaseCommand):
    help = 'Creates an administrator user'

    def handle(self, *args, **kwargs):
        username = 'danielabernales'
        email = 'soundoffchap@gmail.com'

        with transaction.atomic():
            # Check if user already exists
            if User.objects.filter(username=username).exists():
                self.stdout.write(self.style.WARNING(f'User {username} already exists. Updating profile...'))
                user = User.objects.get(username=username)
            else:
                # Create the user
                user = User.objects.create_user(
                    username=username,
                    email=email,
                    password='danielabernales123',
                    first_name='Daniela',
                    last_name='Bernales'
                )
                self.stdout.write(self.style.SUCCESS(f'Created user: {username}'))
            
            # Create or update the user profile
            profile, created = UserProfile.objects.update_or_create(
                user=user,
                defaults={'role': UserProfile.Role.ADMINISTRATOR}
            )
            
            if created:
                self.stdout.write(self.style.SUCCESS('Created administrator profile'))
            else:
                self.stdout.write(self.style.SUCCESS('Updated administrator profile'))
            
            self.stdout.write(self.style.SUCCESS(f'Successfully set up administrator user: {username}'))
