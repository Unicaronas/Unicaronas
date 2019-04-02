from django.core.mail import send_mail
from django.urls import reverse
from django.conf import settings
from project.emailing import build_action_html_message, build_action_txt_message


def approved_student_proof_email(user):
    data = {
        "title": "Aprovamos sua aplicação!",
        "subtitle": "Agora você já pode usar o Unicaronas",
        "description": "Avaliamos e aprovamos os documentos que você enviou comprovando as informações da sua universidade. Você agora já pode acessar sua conta e pegar caronas!",
        "actionUrl": settings.ROOT_URL + reverse('profile'),
        "actionName": "Ir para sua conta"
    }

    html = build_action_html_message(**data)
    text = build_action_txt_message(**data)
    send_mail(
        f"[{settings.PROJECT_NAME}] Aplicação aprovada",
        text,
        settings.DEFAULT_FROM_EMAIL,
        [user.email],
        html_message=html
    )
