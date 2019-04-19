import calendar

from rest_framework import serializers
from oauth2_provider.models import get_access_token_model, get_refresh_token_model, get_application_model


def unixtime(dt):
    return int(calendar.timegm(dt.timetuple()))


class TokenMetadataSerializer(serializers.ModelSerializer):
    client_type = serializers.CharField(source='application.client_type')
    grant_type = serializers.CharField(source='application.authorization_grant_type')

    class Meta:
        model = get_access_token_model()
        fields = ('client_type', 'grant_type')


class DebugTokenSerializer(serializers.ModelSerializer):
    client_id = serializers.CharField(source='application.client_id')
    application = serializers.CharField(source='application.name')
    user_id = serializers.CharField(source='scoped_user_id')
    expires_at = serializers.SerializerMethodField()
    issued_at = serializers.SerializerMethodField()
    scopes = serializers.CharField(source='scope')
    metadata = TokenMetadataSerializer(source='*')

    def get_expires_at(self, data):
        return unixtime(self.instance.expires)

    def get_issued_at(self, data):
        return unixtime(self.instance.created)

    class Meta:
        model = get_access_token_model()
        fields = ('client_id', 'application', 'expires_at', 'is_expired', 'issued_at', 'scopes', 'user_id', 'metadata')


class DebugRefreshokenSerializer(serializers.ModelSerializer):
    client_id = serializers.CharField(source='application.client_id')
    application = serializers.CharField(source='application.name')
    user_id = serializers.SerializerMethodField()
    issued_at = serializers.SerializerMethodField()
    is_revoked = serializers.SerializerMethodField()

    def get_expires_at(self, data):
        return unixtime(self.instance.expires)

    def get_issued_at(self, data):
        return unixtime(self.instance.created)

    def get_is_revoked(self, data):
        return bool(self.instance.revoked)

    def get_user_id(self, data):
        return get_application_model().get_scoped_user_id(self.instance.application, self.context['request'].user)

    class Meta:
        model = get_refresh_token_model()
        fields = ('client_id', 'application', 'is_revoked', 'issued_at', 'user_id')
