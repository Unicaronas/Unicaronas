from datetime import timedelta
from django.utils import timezone
from oauth2_provider.oauth2_validators import OAuth2Validator
from oauth2_provider.settings import oauth2_settings
from oauth2_provider.models import get_grant_model, get_application_model

Grant = get_grant_model()
Application = get_application_model()


class PKCEOAuth2Validator(OAuth2Validator):

    def save_authorization_code(self, client_id, code, request, *args, **kwargs):
        expires = timezone.now() + timedelta(
            seconds=oauth2_settings.AUTHORIZATION_CODE_EXPIRE_SECONDS)
        g = Grant(
            application=request.client,
            user=request.user,
            code=code["code"],
            expires=expires,
            redirect_uri=request.redirect_uri,
            scope=" ".join(request.scopes),
            code_challenge=request.code_challenge,
            code_challenge_method=request.code_challenge_method
        )
        g.save()

    def validate_code(self, client_id, code, client, request, *args, **kwargs):
        try:
            grant = Grant.objects.get(code=code, application=client)

            code_verifier = request.extra_credentials['code_verifier']
            if client.client_type == Application.CLIENT_PUBLIC and not grant.verify_code_challenge(code_verifier):
                # Code verifier does not match the one sent during the authorize call
                return False

            if not grant.is_expired():
                request.scopes = grant.scope.split(" ")
                request.user = grant.user
                return True
            return False

        except Grant.DoesNotExist:
            return False
