from django import template

register = template.Library()


@register.simple_tag
def approved_scopes(app, user):
    return app.approved_scopes(user)
