from django.core.management import call_command
from celery import shared_task


@shared_task
def clear_oauth_tokens():
    call_command('cleartokens')
