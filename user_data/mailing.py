from django.core.mail import send_mail
from django.urls import reverse
from django.conf import settings
from project.emailing import build_action_html_message, build_action_txt_message, build_basic_html_message, build_basic_txt_message


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


def fake_user_warn_email(user):
    data = {
        "title": "Tudo bem?",
        "subtitle": "",
        "description": "Detectamos que você criou uma conta com um RA que não é seu: {user.student.university_id}. Isso fere a essência do Unicaronas e, por isso, desativamos sua conta. Caso você acredite que recebeu essa mensagem por engano, basta responder esse email explicando o que aconteceu."
    }

    html = build_basic_html_message(**data)
    text = build_basic_txt_message(**data)
    send_mail(
        f"[{settings.PROJECT_NAME}] Sua conta foi desativada",
        text,
        settings.DEFAULT_FROM_EMAIL,
        [user.email],
        html_message=html
    )
