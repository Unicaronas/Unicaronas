from rest_framework import serializers
from project.mixins import PrefetchMixin, QueryFieldsMixin
from project.utils import import_current_version_module, local_versioned_url_name
from search.pipeline import RequestPipeline
from ....models import Alarm

PointSerializer = import_current_version_module('trips', 'serializers').PointSerializer


class AlarmCreateSerializer(serializers.HyperlinkedModelSerializer):
    """
    Base Serializer for the creation of alarms
    """

    origin = serializers.CharField(label='Endereço de origem do alarme', required=True)
    destination = serializers.CharField(label='Endereço de destino do alarme', required=True)

    def create(self, validated_data):
        user = self.context['request'].user
        validated_data['user'] = user
        return super().create(validated_data)

    def validate(self, data):
        data = super().validate(data)

        if data.get('origin'):
            pipe_origin = RequestPipeline(query_type='origin', request=self.context['request'])
            result_origin = pipe_origin.search(data['origin'])
            data['origin'] = result_origin.address
            data['origin_point'] = result_origin.point

        if data.get('destination'):
            pipe_destination = RequestPipeline(query_type='destination', request=self.context['request'])
            result_destination = pipe_destination.search(data['destination'])
            data['destination'] = result_destination.address
            data['destination_point'] = result_destination.point
        return data

    class Meta:
        model = Alarm
        fields = [
            'origin', 'destination', 'origin_radius', 'destination_radius', 'price',
            'auto_approve', 'datetime_lte', 'datetime_gte', 'min_seats'
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

    class Meta:
        model = Alarm
        fields = [
            'url', 'origin', 'destination', 'origin_coordinates',
            'destination_coordinates', 'origin_radius', 'destination_radius',
            'price', 'datetime_lte', 'datetime_gte', 'auto_approve',
            'min_seats'
        ]
        extra_kwargs = {
            'origin': {'required': False},
            'destination': {'required': False},
            'price': {'required': False},
            'datetime_lte': {'required': False},
            'datetime_gte': {'required': False},
            'auto_approve': {'required': False},
            'min_seats': {'required': False},
        }
