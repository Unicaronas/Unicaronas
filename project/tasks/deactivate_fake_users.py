from celery import shared_task
from user_data.management.commands.deactivate_fake_users import deactivate_fake_users as dfu


@shared_task
def deactivate_fake_users():
    dfu(True)
