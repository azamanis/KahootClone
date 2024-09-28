from models.models import User
from django.core.management.base import BaseCommand
import os


class Command(BaseCommand):
    help = ('Creates a superuser using the environment variables'
            'DJANGO_SU_NAME and DJANGO_SU_PASSWORD')

    def handle(self, *args, **options):
        # Author: Pablo Cuesta Sierra
        username = os.environ.get('DJANGO_SU_NAME', 'admin')
        if not User.objects.filter(username=username).exists():
            User.objects.create_superuser(
                username=username,
                password=os.environ.get('DJANGO_SU_PASSWORD', 'password'),
            )
            print('Superuser has been created.')
        else:
            print('Superuser already existed.')
