from oauthlib.oauth2 import InvalidRequestError, OAuth2Error
from oauth2_provider.oauth2_backends import OAuthLibCore
from oauth2_provider.exceptions import OAuthToolkitError
from oauth2_provider.models import get_grant_model

Grant = get_grant_model()


class PKCEOAuthLibCore(OAuthLibCore):

    def _get_extra_credentials(self, request):
        """
        Produce extra credentials for token response. This dictionary will be
        merged with the response.
        See also: `oauthlib.oauth2.rfc6749.TokenEndpoint.create_token_response`
        :param request: The current django.http.HttpRequest object
        :return: dictionary of extra credentials or None (default)
        """
        extra_credentials = {
            'code_verifier': request.POST.get('code_verifier', None)
        }
        return extra_credentials

    def _validate_code_challenge_and_method(self, request, credentials):
        """
        Extract and validate the code_challenge and code_challenge_method.
        These values will then be added to the credentials from validate_authorization_request
         :param credentials: dictionary of credentials returned from
                            server.validate_authorization_request
        :param request: The current django.http.HttpRequest object
        :return: The tuple (code_challenge, code_challenge_method)
        """
        code_challenge = request.GET.get("code_challenge", None)
        code_challenge_method = request.GET.get("code_challenge_method", None)
        check = [code_challenge, code_challenge_method]
        error = InvalidRequestError()
        error.redirect_uri = credentials["redirect_uri"]
        if not any(check):
            # If none are set, return them
            return code_challenge, code_challenge_method
        elif not all(check):
            """
            If code_challenge or code_challenge_method is defined, but not the other,
            raise an error per spec
            """
            error.description = "PKCE requires both `code_challenge` and `code_challenge_method` to be set"
            raise error
        if 43 > len(code_challenge) or len(code_challenge) > 128:
            # If the code_challenge length does not meet spec
            error.description = "invalid code_challenge length"
            raise error
        if code_challenge_method not in map(lambda x: x[0], Grant.CODE_CHALLENGE_METHODS):
            # Validate transform algorithm
            error.description = "transform algorithm not supported"
            raise error
        return code_challenge, code_challenge_method

    def validate_authorization_request(self, request):
        scopes, credentials = super().validate_authorization_request(request)

        try:
            code_challenge, code_challenge_method = self._validate_code_challenge_and_method(
                request, credentials)
        except OAuth2Error as e:
            raise OAuthToolkitError(error=e)
        credentials["code_challenge"] = code_challenge
        credentials["code_challenge_method"] = code_challenge_method
        return scopes, credentials
