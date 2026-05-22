from django.contrib.auth.signals import user_logged_in
from django.dispatch import receiver

from .models import LoginEvent


def _get_client_ip(request):
    if not request:
        return None

    x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
    if x_forwarded_for:
        return x_forwarded_for.split(',')[0].strip()

    return request.META.get('REMOTE_ADDR')


@receiver(user_logged_in)
def log_user_login(sender, request, user, **kwargs):
    LoginEvent.objects.create(
        user=user,
        ip_address=_get_client_ip(request),
        user_agent=(request.META.get('HTTP_USER_AGENT', '') if request else ''),
    )
