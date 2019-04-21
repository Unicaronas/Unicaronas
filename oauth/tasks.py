from django.contrib.auth.models import User
from django.db import transaction
from django.utils import timezone
from celery import shared_task
from oauth2_provider.models import get_application_model, get_refresh_token_model, get_access_token_model, clear_expired


@shared_task
def clear_oauth_tokens():
    clear_expired()


@shared_task
def revoke_tokens(app_id, user_id):
    app = get_application_model().objects.filter(id=app_id)
    user = User.objects.get(pk=user_id)
    if app.exists():
        app = app.first()
        with transaction.atomic():
            access_tokens = get_access_token_model().objects.filter(
                user=user,
                application=app
            )
            refresh_tokens = get_refresh_token_model().objects.filter(
                user=user,
                application=app
            )
            access_tokens.delete()
            refresh_tokens.update(revoked=timezone.now())
