import re
from django.core.validators import RegexValidator


class BaseValidator(object):
    def __call__(self, field, value, *args, **kwargs):
        self.message = self.message.format(field)
        super().__call__(value)


class UniversityRegexValidator(
        BaseValidator,
        RegexValidator):

    def __init__(self, regex=None, message=None, code=None, inverse_match=None, flags=re.I):
        super().__init__(regex, message, code, inverse_match, flags)
