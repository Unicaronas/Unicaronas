from celery import shared_task
import requests


@shared_task
def send_webhook(recipient, data, timeout=5):

    requests.post(
        recipient,
        json=data,
        timeout=timeout,
        allow_redirects=False,
        verify=True
    )
