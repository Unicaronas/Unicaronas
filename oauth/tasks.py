from django.contrib.auth.models import User
from django.core.management import call_command
from celery import shared_task
from oauth2_provider.models import get_application_model, get_refresh_token_model, get_access_token_model


@shared_task
def clear_oauth_tokens():
    call_command('cleartokens')


@shared_task
def revoke_tokens(app_id, user_id):
    app = get_application_model().objects.filter(id=app_id)
    user = User.objects.get(pk=user_id)
    if app.exists():
        app = app.first()
        refresh_tokens = get_refresh_token_model().objects.filter(
            user=user,
            application=app
        )
        for token in refresh_tokens:
            token.revoke()
        access_tokens = get_access_token_model().objects.filter(
            user=user,
            application=app
        )
        for token in access_tokens:
            token.revoke()
