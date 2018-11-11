from django.db.models import Prefetch
from rest_framework import serializers
from drf_yasg.utils import swagger_serializer_method
from project.utils import local_versioned_url_name
from project.mixins import PrefetchMixin, QueryFieldsMixin
from oauth.fields import ScopedUserIDField, NestedScopedUserIDHyperlinkedField
from user_data.api.versions.v1_0.serializers import NotPermissionedProfileSerializer, BasicStudentSerializer, BasicProfileSerializer
from .trip import BaseTripListRetrieveSerializer
from .driver import DriverDetailedInfo, DriverBasic2Info
from .....models import Passenger, STATUS_CHOICES


class BasicPassengerSerializer(
        QueryFieldsMixin,
        PrefetchMixin,
        serializers.HyperlinkedModelSerializer):
    """
    Passenger serializer for passengers
    Used when displaying information about passengers to other passengers on a trip
    """
    user_id = ScopedUserIDField(
        source='user',
        label='ID do passageiro'
    )
    first_name = serializers.CharField(
        source='user.first_name',
        required=False
    )
    profile = BasicProfileSerializer(
        source='user.profile',
        label="Perfil do passageiro",
        required=False
    )
    student = BasicStudentSerializer(
        source='user.student',
        label="Informações de estudante do passageiro",
        required=False
    )

    class Meta:
        model = Passenger
        fields = ['user_id', 'first_name', 'profile', 'student', 'seats']
        select_related_fields = ['user', 'user__profile', 'user__student']


class PassengerTripListRetrieveSerializer(BaseTripListRetrieveSerializer):
    """
    Shows details of a trip and its driver to passenger who have been accepted into it
    """
    url = serializers.HyperlinkedIdentityField(
        label="URL para detalhes da carona",
        view_name=local_versioned_url_name(
            'api:passenger-trips-detail', __file__, 2)
    )
    driver = DriverDetailedInfo(help_text="Dados completos do motorista. Disponível se o passageiro **tiver** sido aprovado na carona.", source='user', required=False)
    driver_basic = DriverBasic2Info(help_text="Dados básicos do motorista. Disponível se o passageiro **não tiver** sido aprovado na carona.", source='user', required=False)
    status = serializers.SerializerMethodField(help_text="Status do passageiro na carona")
    seats = serializers.SerializerMethodField(help_text="Número de assentos reservados")
    approved_passengers = BasicPassengerSerializer(help_text="Passageiros aprovados na carona. Disponível se o passageiro **tiver** sido aprovado na carona.", many=True, required=False)

    @swagger_serializer_method(serializer_or_field=serializers.ChoiceField(choices=STATUS_CHOICES))
    def get_status(self, obj):
        user = self.context['request'].user
        passenger = obj.passengers.filter(user=user).first()
        return passenger.status if passenger is not None else None

    @swagger_serializer_method(serializer_or_field=serializers.IntegerField())
    def get_seats(self, obj):
        user = self.context['request'].user
        passenger = obj.passengers.filter(user=user).first()
        return passenger.seats if passenger is not None else None

    @classmethod
    def setup_eager_loading(cls, queryset):
        queryset = super().setup_eager_loading(queryset)
        approved_passengers = Passenger.objects.filter(status='approved').select_related('user__driver', 'user__profile', 'user__student')
        queryset = queryset.prefetch_related(
            Prefetch('passengers', to_attr='approved_passengers', queryset=approved_passengers)
        )
        return queryset

    def to_representation(self, obj):
        # get the original representation
        representation = super().to_representation(obj)

        # If the user status is not approved, pop some fields
        if representation['status'] != 'approved':
            representation.pop('driver')
            representation.pop('approved_passengers')
        else:
            representation.pop('driver_basic')

        return representation

    class Meta(BaseTripListRetrieveSerializer.Meta):
        fields = BaseTripListRetrieveSerializer.Meta.fields + \
            ['url', 'status', 'seats', 'driver', 'driver_basic', 'approved_passengers']
        select_related_fields = ['user__driver', 'user__profile', 'user__student']


class PassengerSerializer(
        QueryFieldsMixin,
        PrefetchMixin,
        serializers.HyperlinkedModelSerializer):
    """
    Passenger serializer to drivers
    Shows up when a driver is viewing who asked to join their trip
    """
    user_id = ScopedUserIDField(
        source='user',
        label='ID do passageiro'
    )
    url = NestedScopedUserIDHyperlinkedField(
        label="Detalhes do passageiro",
        lookup_url_kwarg='passenger_user_id',
        parent_lookup_kwargs={'trip_id': 'trip__id'},
        view_name=local_versioned_url_name(
            'api:driver-trips-passengers-detail', __file__, 2)
    )
    trip = serializers.HyperlinkedRelatedField(
        label="Detalhes da carona",
        lookup_url_kwarg='id',
        read_only=True,
        view_name=local_versioned_url_name(
            'api:driver-trips-detail', __file__, 2)
    )
    first_name = serializers.CharField(
        source='user.first_name',
        required=False
    )
    last_name = serializers.CharField(
        source='user.last_name',
        required=False
    )
    profile = NotPermissionedProfileSerializer(
        source='user.profile',
        label="Perfil do passageiro",
        required=False
    )
    student = BasicStudentSerializer(
        source='user.student',
        label="Informações de estudante do passageiro",
        required=False
    )

    class Meta:
        model = Passenger
        fields = ['url', 'trip', 'user_id', 'first_name', 'last_name',
                  'profile', 'student', 'status', 'seats', 'book_time']
        select_related_fields = ['user', 'user__profile', 'user__student']
        extra_kwargs = {
            'status': {'label': 'Status do passageiro na carona (aprovado, pendente ou negado)'}
        }
