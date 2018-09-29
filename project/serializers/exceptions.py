from rest_framework import serializers


class ExceptionSerializer(serializers.Serializer):
    status_code = serializers.IntegerField()
    detail = serializers.CharField()
