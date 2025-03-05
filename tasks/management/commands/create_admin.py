from django.core.management.base import BaseCommand
from django.contrib.auth.models import User
from tasks.models import UserProfile

class Command(BaseCommand):
    help = 'Creates an administrator user'

    def handle(self, *args, **options):
        try:
            # Create user
            user = User.objects.create_user(
                username='daniela.bernales',
                email='daniela.bernales@example.com',
                password='secure_password_123'
            )

            # Create user profile with administrator role
            UserProfile.objects.create(
                user=user,
                role=UserProfile.Role.ADMINISTRATOR
            )

            self.stdout.write(
                self.style.SUCCESS('Successfully created administrator user')
            )
        except Exception as e:
            self.stdout.write(
                self.style.ERROR(f'Error creating administrator user: {str(e)}')
            )