from django.core.management.base import BaseCommand
from Auth.models import User
from django.conf import settings

class Command(BaseCommand):
    help = 'Create a superuser if it doesn\'t already exist'
    
    def handle(self, *args, **kwargs):
        if not User.objects.filter(name='moundher').exists():
            User.objects.create_superuser(
                name='moundher',
                email=settings.EMAIL_HOST_USER,
                password=settings.PASSWORD,
            )
            self.stdout.write(self.style.SUCCESS('Superuser created successfully'))
        else:
            self.stdout.write(self.style.SUCCESS('Superuser already exists'))
