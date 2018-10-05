from celery import shared_task
from django.conf import settings
from django.shortcuts import reverse
from django.contrib.auth.models import User
from oauth2_provider.models import get_application_model
from project.emailing import send_many_identical_emails, build_action_html_message, build_action_txt_message


def get_new_app_published_params(app):
    subject = f"Novo aplicativo para {app.platform}!"
    title = f"{app.name} foi publicado"
    subtitle = "Vai lá testar ele :)"
    description = f"{app.name}, criado por {app.user.get_full_name()}, acabou de ser publicado. Ele foi feito para {app.platform} e mal pode esperar para ser testado por você!<br>Leia a descrição dele:<br><br>{' '.join(app.description.split()[:20])}{'...' if len(app.description.split()) > 20 else ''}"
    actionUrl = f"{settings.ROOT_URL}{reverse('apps_detail', kwargs={'pk': app.id})}"
    actionName = f"Ver {app.name}!"
    return subject, title, subtitle, description, actionUrl, actionName


@shared_task
def new_app_published(app_id):
    """Takes an app id, finds which users
    should receive the email and then sends them
    """
    app = get_application_model().objects.get(id=app_id)
    subject, title, subtitle, description, actionUrl, actionName = get_new_app_published_params(app)
    text = build_action_txt_message(title, subtitle, description, actionUrl, actionName)
    html = build_action_html_message(title, subtitle, description, actionUrl, actionName)
    recipients = list(User.objects.filter(preferences__news_notifications=True).values_list('email', flat=True))

    send_many_identical_emails(subject, text, html, recipients)
