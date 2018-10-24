from datetime import datetime
from django import template
from django.utils import timezone
from oauth2_provider.models import get_application_model

register = template.Library()


@register.simple_tag
def approved_scopes(app, user):
    return app.approved_scopes(user)


@register.filter
def obfuscate_user_count(app):
    count_map = (
        (1e1, "Menos que 10"),
        (1e2, "Menos que 100"),
        (1e3, "Mais que 100"),
        (1e4, "Mais que 1K"),
        (1e5, "Mais que 10K"),
        (1e6, "Mais que 100K"),
        (1e7, "Mais que 1M"),
    )
    if not isinstance(app, get_application_model()):
        user_count = 0
    else:
        user_count = app.get_users().count()
    return next(filter(lambda x: x[0] > user_count, count_map))[1]


@register.filter
def humanize_created(app):
    time_map = (
        (7, lambda date: "menos que 1 semana"),
        (14, lambda date: "1 semana"),
        (30, lambda date: f"{(timezone.now() - date).days // 7} semanas"),
        (60, lambda date: f"1 mês"),
        (90, lambda date: f"{(timezone.now() - date).days // 30} meses"),
        (365, lambda date: f"1 ano"),
        (1e100, lambda date: f"{(timezone.now() - date).days // 365} anos"),
    )

    if not hasattr(app, 'created') or not isinstance(app.created, datetime):
        time = timezone.now()
    else:
        time = app.created
    return next(filter(lambda x: x[0] > (timezone.now() - time).days, time_map))[1](time)
