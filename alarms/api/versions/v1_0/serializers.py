from rest_framework import serializers
from project.mixins import PrefetchMixin, QueryFieldsMixin
from project.utils import local_versioned_url_name
from project.serializers import PointSerializer
from search.pipeline import RequestPipeline
from ....models import Alarm


class AlarmCreateSerializer(serializers.HyperlinkedModelSerializer):
    """
    Base Serializer for the creation of alarms
    """

    origin = serializers.CharField(
        label='Endereço de origem do alarme', required=True)
    destination = serializers.CharField(
        label='Endereço de destino do alarme', required=True)

    datetime__gte = serializers.DateTimeField(
        label="Datetime máxima de saída da carona", source="datetime_gte", required=False)
    datetime__lte = serializers.DateTimeField(
        label="Datetime máxima de saída da carona", source="datetime_lte", required=False)
    seats_left__gte = serializers.IntegerField(
        label='Mínimo número de assentos na carona', source="min_seats", required=False)
    price__lte = serializers.IntegerField(
        label='Preço máximo da carona em reais', source="price", required=False)

    def create(self, validated_data):
        user = self.context['request'].user
        validated_data['user'] = user
        return super().create(validated_data)

    def validate(self, data):
        data = super().validate(data)

        if data.get('seats_left__gte'):
            data['min_seats'] = data.pop('seats_left__gte')

        if data.get('datetime__lte'):
            data['datetime_lte'] = data.pop('datetime__lte')

        if data.get('datetime__gte'):
            data['datetime_gte'] = data.pop('datetime__gte')

        if data.get('price__lte'):
            data['price'] = data.pop('price__lte')

        if data.get('origin'):
            pipe_origin = RequestPipeline(
                query_type='origin', request=self.context['request'])
            result_origin = pipe_origin.search(data['origin'])
            data['origin'] = result_origin.address
            data['origin_point'] = result_origin.point

        if data.get('destination'):
            pipe_destination = RequestPipeline(
                query_type='destination', request=self.context['request'])
            result_destination = pipe_destination.search(data['destination'])
            data['destination'] = result_destination.address
            data['destination_point'] = result_destination.point
        return data

    class Meta:
        model = Alarm
        fields = [
            'origin', 'destination', 'origin_radius', 'destination_radius', 'price__lte',
            'auto_approve', 'datetime__lte', 'datetime__gte', 'seats_left__gte'
        ]


class AlarmListRetrieveSerializer(
        QueryFieldsMixin,
        PrefetchMixin,
        serializers.HyperlinkedModelSerializer):
    """Alarm list and retrieve serializer
    """
    origin_coordinates = PointSerializer(
        label="Coordenadas da origem",
        source='origin_point',
        required=False
    )
    destination_coordinates = PointSerializer(
        label="Coordenadas do destino",
        source='destination_point',
        required=False
    )

    url = serializers.HyperlinkedIdentityField(
        lookup_url_kwarg='id',
        label="URL para detalhes do alarme",
        view_name=local_versioned_url_name('api:alarms-detail', __file__, 1)
    )

    datetime__gte = serializers.DateTimeField(
        label="Datetime máxima de saída da carona",
        source="datetime_gte",
        required=False
    )
    datetime__lte = serializers.DateTimeField(
        label="Datetime máxima de saída da carona",
        source="datetime_lte",
        required=False
    )
    seats_left__gte = serializers.IntegerField(
        label='Mínimo número de assentos na carona',
        source="min_seats",
        required=False
    )
    price__lte = serializers.IntegerField(
        label='Preço máximo da carona em reais',
        source="price",
        required=False
    )

    class Meta:
        model = Alarm
        fields = [
            'url', 'id', 'origin', 'destination', 'origin_coordinates',
            'destination_coordinates', 'origin_radius', 'destination_radius',
            'price__lte', 'datetime__lte', 'datetime__gte', 'auto_approve',
            'seats_left__gte'
        ]
        extra_kwargs = {
            'origin': {'required': False},
            'destination': {'required': False},
            'auto_approve': {'required': False},
        }
