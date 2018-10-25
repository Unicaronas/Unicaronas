from django.utils import timezone
from rest_framework import serializers
from project.utils import local_versioned_url_name
from third_parties.utils import get_search_keys
from .trip import BaseTripListRetrieveSerializer
from .driver import DriverBasicInfo


class SearchTripSerializer(BaseTripListRetrieveSerializer):
    """Resultado de pesquisa interna
    Mostra informações básicas sobre a carona e seu motorista a futuros passageiros
    que estão procurando caronas
    """
    url = serializers.HyperlinkedIdentityField(
        label="URL para detalhes da carona",
        view_name=local_versioned_url_name(
            'api:search-trips-detail', __file__, 2)
    )
    driver = DriverBasicInfo(source='user')

    class Meta(BaseTripListRetrieveSerializer.Meta):
        select_related_fields = ['user__driver', 'user__profile', 'user__student']
        fields = BaseTripListRetrieveSerializer.Meta.fields + ['driver', 'url']


class ThirdPartyQuerySerializer(serializers.Serializer):
    origin = serializers.CharField(
        required=True,
        help_text="Origem da carona"
    )
    destination = serializers.CharField(
        required=True,
        help_text='Destino da carona'
    )
    price_lte = serializers.IntegerField(
        required=True,
        help_text='Preço máximo da carona'
    )
    datetime_gte = serializers.DateTimeField(
        required=True,
        help_text='Data e hora mínima para saída da carona'
    )
    datetime_lte = serializers.DateTimeField(
        required=True,
        help_text='Data e hora máxima para saída da carona'
    )
    sources = serializers.CharField(
        required=False,
        help_text=f"Fontes das caronas. Lista separada por espaços com as opções `{', '.join(get_search_keys())}`, ou `all` para todas. `all` por padrão"
    )

    def validate_datetime_gte(self, value):
        return max(timezone.now(), value)

    def validate_datetime_lte(self, value):
        return max(timezone.now(), value)

    def validate(self, data):
        if data['datetime_lte'] < data['datetime_gte']:
            raise serializers.ValidationError("'datetime_gte' deve ser antes que 'datetime_lte'")
        return data
