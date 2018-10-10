from django.core.files.images import get_image_dimensions
from django.core.exceptions import ValidationError
from django.core.validators import BaseValidator, URLValidator, _lazy_re_compile
import re
from urllib.parse import urlsplit, urlunsplit
from django.utils.deconstruct import deconstructible


class MaxImageDimensionsValidator(BaseValidator):
    message = 'Sua imagem pode ter no máximo %(limit_height)s px de altura e %(limit_width)s px de largura (ela tem %(show_height)s por %(show_width)s).'
    code = 'image_max_dimensions'

    def __init__(self, limit_width, limit_height, message=None):
        self.limit_height = limit_height
        self.limit_width = limit_width
        if message:
            self.message = message

    def __call__(self, value):
        width, height = get_image_dimensions(value.file)
        cleaned_width, cleaned_height = self.clean(width, height)
        params = {'limit_height': self.limit_height, 'limit_width': self.limit_width, 'show_height': cleaned_height, 'show_width': cleaned_width, 'height': height, 'width': width}
        if self.compare((cleaned_width, cleaned_height), (self.limit_width, self.limit_height)):
            raise ValidationError(self.message, code=self.code, params=params)

    def __eq__(self, other):
        return (
            isinstance(other, self.__class__) and
            self.limit_height == other.limit_height and
            self.limit_width == other.limit_width and
            self.message == other.message and
            self.code == other.code
        )

    def compare(self, cleaned, limit):
        return cleaned[0] > limit[0] or cleaned[1] > limit[1]

    def clean(self, width, height):
        return width, height


class MinImageDimensionsValidator(MaxImageDimensionsValidator):
    message = 'Sua imagem pode ter no mínimo %(limit_height)s px de altura e %(limit_width)s px de largura (ela tem %(show_height)s por %(show_width)s).'
    code = 'image_min_dimensions'

    def compare(self, cleaned, limit):
        return cleaned[0] < limit[0] or cleaned[1] < limit[1]


class SquareImageValidator(BaseValidator):
    message = 'Sua imagem deve ser quadrada (ela tem %(show_height)s por %(show_width)s px).'
    code = 'image_square'

    def __init__(self, message=None):
        if message:
            self.message = message

    def __call__(self, value):
        width, height = get_image_dimensions(value.file)
        cleaned_width, cleaned_height = self.clean(width, height)
        params = {'show_height': cleaned_height, 'show_width': cleaned_width, 'height': height, 'width': width}
        if self.compare((cleaned_width, cleaned_height)):
            raise ValidationError(self.message, code=self.code, params=params)

    def __eq__(self, other):
        return (
            isinstance(other, self.__class__) and
            self.message == other.message and
            self.code == other.code
        )

    def compare(self, cleaned):
        return cleaned[0] != cleaned[1]

    def clean(self, width, height):
        return width, height


class CustomURLValidator(URLValidator):
    ul = '\u00a1-\uffff'  # unicode letters range (must not be a raw string)

    # IP patterns
    ipv4_re = r'(?:25[0-5]|2[0-4]\d|[0-1]?\d?\d)(?:\.(?:25[0-5]|2[0-4]\d|[0-1]?\d?\d)){3}'
    ipv6_re = r'\[[0-9a-f:\.]+\]'  # (simple regex, validated later)

    # Host patterns
    hostname_re = r'[a-z' + ul + r'0-9](?:[a-z' + ul + r'0-9-]{0,61}[a-z' + ul + r'0-9])?'
    # Max length for domain name labels is 63 characters per RFC 1034 sec. 3.1
    domain_re = r'(?:\.(?!-)[a-z' + ul + r'0-9-]{1,63}(?<!-))*'
    tld_re = (
        r'\.'                                # dot
        r'(?!-)'                             # can't start with a dash
        r'(?:[a-z' + ul + '-]{2,63}'         # domain label
        r'|xn--[a-z0-9]{1,59})'              # or punycode label
        r'(?<!-)'                            # can't end with a dash
        r'\.?'                               # may have a trailing dot
    )
    host_re = '(' + hostname_re + domain_re + tld_re + ')'

    loopbacks = r'localhost|127(?:\.[0-9]+){0,2}\.[0-9]+|(?:0*\:)*?:?0*1'

    regex = _lazy_re_compile(
        r'^(?:[a-z0-9\.\-\+]*)://'  # scheme is validated separately
        r'(?:\S+(?::\S*)?@)?'  # user:pass authentication
        r'(?!' + loopbacks + r')'  # exclude loopbacks
        r'(?:' + ipv4_re + '|' + ipv6_re + '|' + host_re + ')'
        r'(?::\d{2,5})?'  # port
        r'(?:[/?#][^\s]*)?'  # resource path
        r'\Z', re.IGNORECASE)
    schemes = ['http', 'https']
