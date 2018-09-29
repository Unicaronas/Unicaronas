from rest_framework import serializers
from project.utils import local_versioned_url_name
from project.mixins import PrefetchMixin, QueryFieldsMixin
from oauth.fields import ScopedUserIDField, NestedScopedUserIDHyperlinkedField
from user_data.api.versions.v1_0.serializers import NotPermissionedProfileSerializer, BasicStudentSerializer
from .trip import BaseTripListRetrieveSerializer
from .driver import DriverBasicInfo, DriverDetailedInfo
from .....models import Passenger


class BasicPassengerTripListRetrieveSerializer(BaseTripListRetrieveSerializer):
    """
    Mostra informações básicas sobre a carona e seu motorista a futuros passageiros
    que estão procurando caronas
    """
    url = serializers.HyperlinkedIdentityField(
        label="URL para detalhes da carona",
        lookup_url_kwarg='trip_id',
        view_name=local_versioned_url_name(
            'api:passenger-trip-detail', __file__)
    )
    driver = DriverBasicInfo(source='driver')
    status = serializers.SerializerMethodField()

    def get_status(self, obj):
        user = self.context['request'].user
        passenger = obj.passengers.filter(user=user).first()
        return passenger.status if passenger is not None else None

    class Meta(BaseTripListRetrieveSerializer.Meta):
        fields = BaseTripListRetrieveSerializer.Meta.fields + ['driver', 'url']


class DetailedPassengerTripListRetrieveSerializer(BaseTripListRetrieveSerializer):
    """
    Mostra detalhes de uma carona e seu motorista aos passageiros que já foram
    aceitos nela
    """
    url = serializers.HyperlinkedIdentityField(
        label="URL para detalhes da carona",
        lookup_url_kwarg='trip_id',
        view_name=local_versioned_url_name(
            'api:passenger-my-trips-detail', __file__, 2)
    )
    driver = DriverDetailedInfo(source='driver')
    status = serializers.SerializerMethodField()

    def get_status(self, obj):
        user = self.context['request'].user
        passenger = obj.passengers.filter(user=user).first()
        return passenger.status if passenger is not None else None

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # TODO: Adicionar help_texts aos campos que só aparecem depois de ser aceito na carona
        self.fields['']

    class Meta(BaseTripListRetrieveSerializer.Meta):
        fields = BaseTripListRetrieveSerializer.Meta.fields + \
            ['driver', 'url', 'status']


class PassengerSerializer(
        QueryFieldsMixin,
        PrefetchMixin,
        serializers.HyperlinkedModelSerializer):
    """
    Serializador de passageiros para motoristas
    Aparece para motoristas que estão vendo quem pediu para
    ser passageiro de sua carona
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
        lookup_url_kwarg='trip_id',
        read_only=True,
        view_name=local_versioned_url_name(
            'api:driver-trips-passengers-list', __file__, 2)
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
        fields = ['url', 'trip', 'user_id', 'first_name',
                  'last_name', 'profile', 'student', 'status', 'book_time']
        select_related_fields = ['user', 'user__profile', 'user__student']
        extra_kwargs = {
            'status': {'label': 'Status do passageiro na carona (aprovado, pendente ou negado)'}
        }
