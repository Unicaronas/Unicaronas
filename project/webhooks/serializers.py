from rest_framework import serializers


class BaseWebhookSerializer(serializers.Serializer):
    event = serializers.CharField()
    payload = serializers.DictField()


class WebhookSerializer(BaseWebhookSerializer):
    """Webhook serializer"""
