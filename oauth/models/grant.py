import hashlib
from base64 import urlsafe_b64encode
from django.db import models
from django.core.validators import MinLengthValidator
from django.core.exceptions import ValidationError
from oauth2_provider import models as omodels


class PKCEGrant(omodels.AbstractGrant):

    CODE_CHALLENGE_PLAIN = 'plain'
    CODE_CHALLENGE_S256 = 'S256'

    CODE_CHALLENGE_METHODS = (
        (CODE_CHALLENGE_PLAIN, 'plain'),
        (CODE_CHALLENGE_S256, 'S256')
    )

    code_challenge = models.CharField(max_length=128, blank=True, default="", validators=[MinLengthValidator(43)])
    code_challenge_method = models.CharField(max_length=10, blank=True, default="", choices=CODE_CHALLENGE_METHODS)

    def verify_code_challenge(self, code_verifier):
        """
        Takes a code_verifier and validates it against
        the saved code_challenge
        """
        # Do not validate if no code challenge was set
        if not self.code_challenge:
            return True

        # If the grant has a code_challenge, but no code_verifier was submitted, the request is invalid
        if not code_verifier:
            return False

        if self.code_challenge_method == self.CODE_CHALLENGE_S256:
            new_code_challenge = urlsafe_b64encode(
                hashlib.sha256(code_verifier.encode('utf-8')).hexdigest().encode('utf-8')
            ).decode('utf-8').replace('=', '')
        else:
            new_code_challenge = code_verifier

        return self.code_challenge == new_code_challenge

    def clean(self):
        code_challenge = self.code_challenge
        code_challenge_method = self.code_challenge_method
        check = [code_challenge, code_challenge_method]
        if not(any(check)):
            return
        if any(check) and not all(check):
            raise ValidationError('PKCE requires both `code_challenge` and `code_challenge_method` to be set')
