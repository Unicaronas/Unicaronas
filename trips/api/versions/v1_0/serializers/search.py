from rest_framework import serializers
from project.utils import local_versioned_url_name
from .trip import BaseTripListRetrieveSerializer
from .driver import DriverBasicInfo


class SearchTripSerializer(BaseTripListRetrieveSerializer):
    """
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
