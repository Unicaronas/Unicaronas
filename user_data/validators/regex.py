import re
from django.core.validators import RegexValidator


class UniRegexValidator(RegexValidator):

    def __init__(self, regex=None, message=None, code=None, inverse_match=None, flags=re.I):
        super().__init__(regex, message, code, inverse_match, flags)

    def __call__(self, value, university):
        self.message = self.message.format(university)
        super().__call__(value)
