import re
from django.core.validators import EmailValidator
from .base import UniversityRegexValidator


class UniRegexValidator(UniversityRegexValidator):
    pass


class FallbackUniRegexValidator(UniversityRegexValidator):

    def __init__(self, regex=None, message=None, code=None, inverse_match=None, flags=re.I):
        super().__init__(regex, message, code, inverse_match, flags)

    def __call__(self, field, value, *args, **kwargs):
        # Validate the user data
        if kwargs['student_proof']:
            # If the user submitted a student proof and is validating email, fallback to regular email validation
            EmailValidator(self.message)(value)
        else:
            # Validate regular expression
            super().__call__(field, value, *args, **kwargs)
