from django import template
from django.template.defaultfilters import stringfilter
from django.conf import settings

register = template.Library()


@register.filter
@stringfilter
def versioned_url(name):
    current_version = settings.REST_FRAMEWORK['DEFAULT_VERSION']
    name = name.split(':')
    return ':'.join([name[0], current_version] + name[1:])
