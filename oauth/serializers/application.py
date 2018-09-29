from rest_framework import serializers
from oauth2_provider.models import get_application_model
from oauth2_provider.validators import RedirectURIValidator, WildcardSet
from oauth2_provider.settings import oauth2_settings
from urllib.parse import urlparse


class ApplicationListSerializer(serializers.HyperlinkedModelSerializer):
    url = serializers.HyperlinkedIdentityField(view_name='oauth2_provider:application-detail', lookup_field='client_id')

    class Meta:
        model = get_application_model()
        fields = ('url', 'name', 'description', 'client_id', 'scope', 'website')
        read_only_fields = ('url', 'client_id')


class ApplicationDetailSerializer(serializers.ModelSerializer):

    def validate_redirect_uris(self, data):
        grant = self.initial_data.get('authorization_grant_type', self.Meta.model.GRANT_AUTHORIZATION_CODE)
        grant_types = (
            self.Meta.model.GRANT_AUTHORIZATION_CODE,
            self.Meta.model.GRANT_IMPLICIT,
        )
        redirect_uris = data.strip().split()
        allowed_schemes = set(s.lower() for s in oauth2_settings.ALLOWED_REDIRECT_URI_SCHEMES)
        if not redirect_uris:
            if grant in grant_types:
                raise serializers.ValidationError(
                    "redirect_uris can't be empty with grant_type {grant_type}".format(
                        grant_type=grant
                    )
                )

        validator = RedirectURIValidator(WildcardSet())
        for uri in redirect_uris:
            validator(uri)
            scheme = urlparse(uri).scheme
            if scheme not in allowed_schemes:
                raise serializers.ValidationError(
                    "Unauthorized redirecting scheme: {scheme}".format(
                        scheme=scheme
                    )
                )
        return data.strip()

    def validate_scope(self, data):
        scope = data.strip()
        scopes = data.split()
        if not scopes:
            return scope
        for sc in scopes:
            if sc not in oauth2_settings._SCOPES:
                raise serializers.ValidationError(
                    "Invalid scope: {scope}".format(
                        scope=sc
                    )
                )
        return scope

    class Meta:
        model = get_application_model()
        fields = ('name', 'description', 'client_id', 'client_secret', 'platform', 'redirect_uris', 'client_type', 'authorization_grant_type', 'scope', 'website', 'published', 'logo')
        read_only_fields = ('client_id', 'client_secret')
        extra_kwargs = {
            'redirect_uris': {'default': ''},
        }
