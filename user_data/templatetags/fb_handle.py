from django import template
from django.conf import settings

register = template.Library()


class FacebookHandleNode(template.Node):

    def __init__(self, as_var=None):
        self.fbh_var = settings.FACEBOOK_HANDLE
        self.as_var = as_var

    def render(self, context):

        if self.as_var:
            context[self.as_var] = self.fbh_var
            return ""
        return self.fbh_var


@register.tag(name="facebook_handle")
def facebook_handle(self, token):
    bits = token.split_contents()
    if len(bits) == 3:
        as_var = bits[2]
    else:
        raise template.TemplateSyntaxError(
            "'%s' takes two arguments" % bits[0])

    return FacebookHandleNode(as_var)
