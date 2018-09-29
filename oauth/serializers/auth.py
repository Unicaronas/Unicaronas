import calendar

from rest_framework import serializers
from oauth2_provider.models import get_access_token_model


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
