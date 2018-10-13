from celery import shared_task
from requests_futures.sessions import FuturesSession


def send_webhook(recipient, data, session, timeout=5):

    session.post(
        recipient,
        json=data,
        timeout=timeout,
        allow_redirects=False,
        verify=True
    )


@shared_task
def send_webhooks(recipients, data_list, timeout=5):

    session = FuturesSession(max_workers=10)

    if not isinstance(recipients, (list, tuple)):
        recipients = tuple(recipients)
    if not isinstance(data_list, (list, tuple)):
        data_list = tuple(data_list)

    if len(recipients) != len(data_list):
        raise ValueError('len of recipients should be the same as data_list')

    for recipient, data in zip(recipients, data_list):
        send_webhook(recipient, data, session, timeout)
