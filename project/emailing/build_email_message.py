from django.template.loader import render_to_string
from django.conf import settings


def build_action_txt_message(title, subtitle, description, actionUrl, actionName):
    context = {
        'title': title,
        'subtitle': subtitle,
        'description': description,
        'actionUrl': actionUrl,
        'actionName': actionName,
        'project_url': settings.ROOT_URL,
        'project_name': settings.PROJECT_NAME,
        'facebookHandle': settings.FACEBOOK_HANDLE
    }
    return render_to_string('project/email/action/text.txt', context)


def build_action_html_message(title, subtitle, description, actionUrl, actionName):
    context = {
        'title': title,
        'subtitle': subtitle,
        'description': description,
        'actionUrl': actionUrl,
        'actionName': actionName,
        'project_url': settings.ROOT_URL,
        'project_name': settings.PROJECT_NAME,
        'facebookHandle': settings.FACEBOOK_HANDLE
    }
    return render_to_string('project/email/action/html.html', context)


def build_basic_txt_message(title, subtitle, description):
    context = {
        'title': title,
        'subtitle': subtitle,
        'description': description,
        'project_url': settings.ROOT_URL,
        'project_name': settings.PROJECT_NAME,
        'facebookHandle': settings.FACEBOOK_HANDLE
    }
    return render_to_string('project/email/basic/text.txt', context)


def build_basic_html_message(title, subtitle, description):
    context = {
        'title': title,
        'subtitle': subtitle,
        'description': description,
        'project_url': settings.ROOT_URL,
        'project_name': settings.PROJECT_NAME,
        'facebookHandle': settings.FACEBOOK_HANDLE
    }
    return render_to_string('project/email/basic/html.html', context)
