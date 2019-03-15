from django.core.management import call_command
from celery import shared_task


@shared_task
def clear_alarms():
    call_command('clear_alarms')
