from rest_framework import serializers
from drf_yasg.utils import swagger_serializer_method
from ..utils import get_search_keys


class BaseResultItemSerializer(serializers.Serializer):

    price = serializers.IntegerField(label="Preço da carona")
    datetime = serializers.DateTimeField(label="Data e hora da carona")
    url = serializers.URLField(label="URL para reserva da carona")
    source = serializers.ChoiceField(label="Fonte da carona", choices=get_search_keys())


class BaseResultSerializer(serializers.Serializer):

    count = serializers.SerializerMethodField(label="Número de resultados retornados")
    results = BaseResultItemSerializer(label="Resultados da pesquisa", many=True)

    @swagger_serializer_method(serializers.IntegerField())
    def get_count(self, obj):
        return len(self.validated_data['results'])
