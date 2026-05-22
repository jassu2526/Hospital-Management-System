from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model
from accounts.models import Profile


class Command(BaseCommand):
    help = 'Ensure superuser with ADMIN profile'

    def add_arguments(self, parser):
        parser.add_argument('--username', required=True)
        parser.add_argument('--password', required=True)
        parser.add_argument('--email', default='admin@example.com')
        parser.add_argument('--phone', default=None)

    def handle(self, *args, **options):
        User = get_user_model()
        username = options['username']
        password = options['password']
        email = options['email']
        phone = options['phone']
        u, created = User.objects.get_or_create(username=username, defaults={'email': email})
        u.is_staff = True
        u.is_superuser = True
        u.email = email or u.email
        u.set_password(password)
        u.save()
        if not phone:
            base = '9999999'
            suffix = str(u.id or 0).zfill(3)
            phone = base + suffix
        Profile.objects.update_or_create(user=u, defaults={'role': 'ADMIN', 'phone_number': phone})
        self.stdout.write('CREATED' if created else 'UPDATED')
