from django.contrib.auth.models import User
from rest_framework import serializers
from project.mixins import PrefetchMixin, QueryFieldsMixin
from project.utils import local_versioned_url_name
from user_data.api.versions.v1_0.serializers import BasicStudentSerializer, NotPermissionedProfileSerializer, NotPermissionedDriverSerializer
from user_data.models import Driver
from .trip import BaseTripCreateUpdateSerializer, BaseTripListRetrieveSerializer


class DriverPreferencesSerializer(
        QueryFieldsMixin,
        serializers.ModelSerializer):

    class Meta:
        model = Driver
        fields = ['likes_pets', 'likes_smoking', 'likes_music', 'likes_talking']


class DriverBasicInfo(
        QueryFieldsMixin,
        PrefetchMixin,
        serializers.ModelSerializer):

    student = BasicStudentSerializer(source='student')
    gender = serializers.CharField(
        label="Gênero",
        source='profile.gender',
        read_only=True
    )

    preferences = DriverPreferencesSerializer(source='driver')

    class Meta:
        model = User
        fields = ['first_name', 'student', 'gender', 'preferences']
        read_only_fields = ['first_name']
        select_related_fields = ['profile', 'student', 'driver']


class DriverDetailedInfo(
        QueryFieldsMixin,
        PrefetchMixin,
        serializers.ModelSerializer):

    profile = NotPermissionedProfileSerializer(source='profile')

    student = BasicStudentSerializer(source='student')

    driver = NotPermissionedDriverSerializer(source='driver')

    class Meta:
        model = User
        fields = ['first_name', 'last_name', 'profile', 'student', 'driver']
        read_only_fields = ['first_name']
        select_related_fields = ['profile', 'student', 'driver']


class DriverTripCreateUpdateSerializer(BaseTripCreateUpdateSerializer):
    """Serializer for the creation of trips by drivers"""


class DriverTripListRetrieveSerializer(BaseTripListRetrieveSerializer):
    """Serializer for the viewing of trips by drivers"""

    url = serializers.HyperlinkedIdentityField(
        lookup_url_kwarg='id',
        label="URL para detalhes da carona",
        view_name=local_versioned_url_name('api:driver-trips-detail', __file__, 2)
    )
    passengers = serializers.HyperlinkedIdentityField(
        label="URL para lista de passageiros da carona",
        lookup_url_kwarg='trip_id',
        view_name=local_versioned_url_name('api:driver-trips-passengers-list', __file__, 2)
    )

    class Meta(BaseTripListRetrieveSerializer.Meta):
        fields = ['url', 'passengers'] + BaseTripListRetrieveSerializer.Meta.fields
