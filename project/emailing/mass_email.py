from django.core.mail import get_connection, EmailMultiAlternatives


def send_mass_html_mail(datatuple, fail_silently=False, user=None, password=None,
                        connection=None):
    """
    Given a datatuple of (subject, text_content, html_content, from_email,
    recipient_list), sends each message to each recipient list. Returns the
    number of emails sent.

    If from_email is None, the DEFAULT_FROM_EMAIL setting is used.
    If auth_user and auth_password are set, they're used to log in.
    If auth_user is None, the EMAIL_HOST_USER setting is used.
    If auth_password is None, the EMAIL_HOST_PASSWORD setting is used.

    """
    connection = connection or get_connection(
        username=user, password=password, fail_silently=fail_silently)
    messages = []
    for subject, text, html, from_email, recipient in datatuple:
        recipient = [recipient] if not isinstance(recipient, (list, tuple)) else recipient
        message = EmailMultiAlternatives(subject, text, from_email, recipient)
        message.attach_alternative(html, 'text/html')
        messages.append(message)
    return connection.send_messages(messages)


def send_mass_signed_mail(datatuples):
    """Receives a list of emails to send
    and adds [Unicaronas] to its subject
    before sending
    """
    datatuples = list(datatuples)
    for tup in datatuples:
        tup = list(tup)
        tup[0] = f"[Unicaronas] {tup[0]}"
        tup = tuple(tup)
    datatuples = tuple(datatuples)
    send_mass_html_mail(datatuples)


def send_many_identical_emails(subject, text, html, recipients):
    datatuples = ((subject, text, html, None, email) for email in recipients)
    send_mass_signed_mail(datatuples)
