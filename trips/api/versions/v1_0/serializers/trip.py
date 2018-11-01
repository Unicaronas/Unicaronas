from django.db.models import F, Q, Sum
from django.db.models.functions import Coalesce
from rest_framework import serializers
from project.mixins import PrefetchMixin, QueryFieldsMixin
from search.pipeline import RequestPipeline
from .base import PointSerializer
from .....models import Trip


class BaseTripCreateUpdateSerializer(serializers.HyperlinkedModelSerializer):
    """
    Base Serializer for drivers to create and update trips
    """

    auto_approve = serializers.BooleanField(required=False, default=True)

    def create(self, validated_data):
        user = self.context['request'].user
        app = getattr(self.context['request'].auth, 'application', None)
        validated_data['user'] = user
        validated_data['application'] = app
        return super().create(validated_data)

    def validate(self, data):
        data = super().validate(data)

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
        model = Trip
        fields = [
            'origin', 'destination', 'price', 'datetime', 'auto_approve',
            'max_seats', 'details'
        ]


class BaseTripListRetrieveSerializer(
        QueryFieldsMixin,
        PrefetchMixin,
        serializers.HyperlinkedModelSerializer):
    """Base trip list and retrieve serializer
    Extend to add information about the driver and/or passengers

    Also add URL information for access to details
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

    seats_left = serializers.IntegerField(
        label="Assentos restantes", read_only=True)
    is_full = serializers.BooleanField(
        label="Se a carona está cheia", read_only=True)

    @classmethod
    def setup_eager_loading(cls, queryset):
        queryset = super().setup_eager_loading(queryset)
        seats_left = F('max_seats') - Coalesce(
            Sum(
                'passengers__seats',
                filter=~Q(passengers__status="denied")
            ), 0)
        queryset = queryset.annotate(seats_left=seats_left)
        return queryset

    class Meta:
        model = Trip
        fields = [
            'id', 'origin', 'destination', 'origin_coordinates',
            'destination_coordinates', 'price', 'datetime', 'auto_approve',
            'max_seats', 'seats_left', 'is_full', 'details'
        ]
        extra_kwargs = {
            'id': {'label': 'ID da carona'},
            'origin': {'required': False},
            'destination': {'required': False},
            'price': {'required': False},
            'datetime': {'required': False},
        }
