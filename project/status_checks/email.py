from django.core.mail import EmailMessage, get_connection
from django.core.mail.backends.smtp import EmailBackend
from django.conf import settings
from watchman.decorators import check


# @check
def _check_email():
    conn = get_connection(backend='django.core.mail.backends.smtp.EmailBackend')
    headers = {"X-DJANGO-WATCHMAN": True}
    email = EmailMessage(
        "django-watchman email check",
        "This is an automated test of the email system.",
        headers=headers,
        connection=conn
    )
    email.send()
    return {"ok": True}


def email():
    if not settings.WATCHMAN_ENABLE_PAID_CHECKS:
        return {}
    return {'Email': _check_email()}
