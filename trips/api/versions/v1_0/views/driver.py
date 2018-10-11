from django.utils import timezone
from django.shortcuts import get_object_or_404
from rest_framework import viewsets, status, mixins
from rest_framework.exceptions import ValidationError
from rest_framework.response import Response
from drf_yasg.utils import swagger_auto_schema
from drf_yasg import openapi
from oauth2_provider.contrib.rest_framework.permissions import TokenMatchesOASRequirements
from project.mixins import PrefetchQuerysetModelMixin, PatchModelMixin
from oauth2_provider.models import get_application_model
from oauth.exceptions import InvalidScopedUserId
from user_data.permissions import UserIsDriver
from ..inspectors import DjangoFilterDescriptionInspector
from ..filters import LocalizedOrderingFilter
from ..serializers import DriverTripCreateUpdateSerializer, DriverTripListRetrieveSerializer, PassengerSerializer, DriverActionsSerializer
from .....models import Trip, Passenger
from .....exceptions import PassengerPendingError, PassengerApprovedError, PassengerDeniedError, TripFullError


class DriverTripViewset(
        PrefetchQuerysetModelMixin,
        viewsets.ModelViewSet):
    """Endpoint dos motoristas

    Permite a criação de caronas, listagem de caronas que criou e edição delas
    """
    lookup_field = 'id'
    swagger_tags = ['Motorista']
    queryset = Trip.objects.all()
    max_limit = 50
    limit = 10
    filter_backends = (
        LocalizedOrderingFilter,
    )
    ordering_fields = [
        'price', 'datetime'
    ]
    ordering = ['-datetime', 'price']
    permission_classes = [TokenMatchesOASRequirements, UserIsDriver]
    required_alternate_scopes = {
        "GET": [["trips:driver:read"]],
        "POST": [["trips:driver:write"]],
        "PUT": [["trips:driver:write"]],
        "PATCH": [["trips:driver:write"]],
        "DELETE": [["trips:driver:write"]]
    }

    def get_queryset(self):
        qs = super().get_queryset()
        # Only allow editing and viewing the user's trips
        qs = qs.filter(user=self.request.user)
        # If the trip already happened, only allow GET
        if self.request.method != 'GET':
            qs = qs.filter(datetime__gt=timezone.now())
        return qs

    def get_serializer_class(self):
        if self.request.method == 'GET':
            return DriverTripListRetrieveSerializer
        return DriverTripCreateUpdateSerializer

    @swagger_auto_schema(
        responses={
            400: "Seus parâmetros GET estão mal formatados",
            404: "Carona pesquisada não existe ou você não tem acesso"
        },
        manual_parameters=[
            openapi.Parameter(DriverTripListRetrieveSerializer.include_arg_name, openapi.IN_QUERY,
                              "Seleciona dados retornados, separados por vírgula. Campos aninhados são suportados. Exemplo: `fields=campo1,campo2{sub_campo1, sub_campo2}`", type=openapi.TYPE_STRING),
            openapi.Parameter(DriverTripListRetrieveSerializer.exclude_arg_name, openapi.IN_QUERY,
                              "Exclui dados retornados, separados por vírgula. Campos aninhados são suportados. Exemplo: `exclude=campo1,campo2{sub_campo1, sub_campo2}`", type=openapi.TYPE_STRING)
        ],
        security=[
            {'unicaronas auth': ['trips:driver:read']}
        ]
    )
    def retrieve(self, *args, **kwargs):
        """Detalhar carona

        Permite acessar os dados detalhados de uma carona que está sendo fornecida pelo seu usuário.

        Para acessar, use a `ID` de uma carona que o usuário é motorista.

        > **Dica:** Você também pode usar os parâmetros GET `fields` e `exclude` para filtrar os campos retornados pela API
        """
        return super().retrieve(*args, **kwargs)

    @swagger_auto_schema(
        responses={
            400: "Seus parâmetros GET estão mal formatados",
        },
        manual_parameters=[
            openapi.Parameter('fields', openapi.IN_QUERY,
                              "Seleciona dados retornados, separados por vírgula. Campos aninhados são suportados. Exemplo: `fields=campo1,campo2{sub_campo1, sub_campo2}`", type=openapi.TYPE_STRING),
            openapi.Parameter('exclude', openapi.IN_QUERY,
                              "Exclui dados retornados, separados por vírgula. Campos aninhados são suportados. Exemplo: `exclude=campo1,campo2{sub_campo1, sub_campo2}`", type=openapi.TYPE_STRING)
        ],
        filter_inspectors=[DjangoFilterDescriptionInspector],
        security=[
            {'unicaronas auth': ['trips:driver:read']}
        ]
    )
    def list(self, *args, **kwargs):
        """Listar caronas

        Permite listar todas as caronas que o usuário já criou.

        Esse endpoint suporta ordenação por `price` e por `datetime`.

        > **Dica:** Você também pode usar os parâmetros GET `fields` e `exclude` para filtrar os campos retornados pela API
        """
        return super().list(*args, **kwargs)

    def perform_create(self, serializer):
        return serializer.save()

    @swagger_auto_schema(
        responses={
            201: DriverTripListRetrieveSerializer,
            400: 'Dados do pedido contém erros'
        },
        security=[
            {'unicaronas auth': ['trips:driver:write']}
        ]
    )
    def create(self, request, *args, **kwargs):
        """Criar carona

        Crie caronas pelo usuário.

        A API irá gerar automaticamente os dados faltantes de origem e destino usando a [API de Geocoding do Google](https://developers.google.com/maps/documentation/geocoding/intro).
        Por conta disso, o fornecimento de endereços incorretos poderá resultar em endereços que estarão completamente errados, como em outras cidades ou estados.

        O Unicaronas tenta mitigar isso mapeando endereços digitados com frequência e fazendo correção gramatical dos dados de entrada, mas nem sempre isso será suficiente para corrigir entradas ruins. Dessa forma, garanta que os resultados gerados são os esperados enviando endereços o mais completos possível.
        Gerar endereços completos é difícil, então considere as seguintes opções:
        - Dê opções limitadas de busca aos seus usários. Opções essas cujos endereços completos sejam conhecidos por você. Ex: Unicamp, Posto da 1, Metro Tietê, etc
        - Use uma API como a de [Autocomplete](https://developers.google.com/places/web-service/autocomplete) para gerar endereços completos enquanto o usuário digita

        Nem todos os parâmetros são obrigatórios. Na falta deles, esses serão os padrões:

        | Campo         | Padrão        |
        | --------------|---------------|
        | `auto_approve`| `true`        |
        | `max_seats`   | 4             |
        | `details`     | *em branco*   |
        """
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        instance = self.perform_create(serializer)
        serializer = DriverTripListRetrieveSerializer(instance=instance, context=self.get_serializer_context())
        headers = self.get_success_headers(serializer.data)
        return Response(serializer.data, status=status.HTTP_201_CREATED, headers=headers)

    @swagger_auto_schema(
        responses={
            200: DriverTripListRetrieveSerializer,
            404: 'Carona não existe, já aconteceu, ou você não tem permissão para acessá-la',
            400: 'Dados do pedido contém erros',
        },
        security=[
            {'unicaronas auth': ['trips:driver:write']}
        ]
    )
    def update(self, request, *args, **kwargs):
        """Atualizar carona

        Permite a alteração de dados de caronas que **ainda não aconteceram**. Caso a carona já tenha acontecido, a resposta desse endpoint será um erro *404*.
        """
        partial = kwargs.pop('partial', False)
        instance = self.get_object()
        serializer = self.get_serializer(instance, data=request.data, partial=partial)
        serializer.is_valid(raise_exception=True)
        self.perform_update(serializer)
        serializer = DriverTripListRetrieveSerializer(instance=instance, context=self.get_serializer_context())
        if getattr(instance, '_prefetched_objects_cache', None):
            # If 'prefetch_related' has been applied to a queryset, we need to
            # forcibly invalidate the prefetch cache on the instance.
            instance._prefetched_objects_cache = {}

        return Response(serializer.data)

    @swagger_auto_schema(
        responses={
            200: DriverTripListRetrieveSerializer,
            400: 'Dados do pedido contém erros',
            404: 'Carona não existe, já aconteceu, ou você não tem permissão para acessá-la'
        },
        security=[
            {'unicaronas auth': ['trips:driver:write']}
        ]
    )
    def partial_update(self, *args, **kwargs):
        """Atualizar parcialmente carona

        Permite a alteração de dados de caronas que **ainda não aconteceram**. Caso a carona já tenha acontecido, a resposta desse endpoint será um erro *404*.
        """
        return super().partial_update(*args, **kwargs)

    @swagger_auto_schema(
        responses={
            404: 'Carona não existe, já aconteceu, ou você não tem permissão para acessá-la',
        },
        security=[
            {'unicaronas auth': ['trips:driver:write']}
        ]
    )
    def destroy(self, *args, **kwargs):
        """Apagar carona

        Permite apagar caronas que **ainda não aconteceram**. Caso a carona já tenha acontecido, a resposta desse endpoint será um erro *404*.
        """
        instance = self.get_object()
        instance.delete_trip()
        return Response(status=status.HTTP_204_NO_CONTENT)


class DriverPassengerActionsViewset(
        mixins.RetrieveModelMixin,
        mixins.ListModelMixin,
        PatchModelMixin,
        mixins.DestroyModelMixin,
        viewsets.GenericViewSet):
    """
    Ações que o motorista pode executar nos passageiros de suas caronas
    """
    lookup_url_kwarg = 'passenger_user_id'
    queryset = Passenger.objects.all()
    serializer_class = PassengerSerializer
    swagger_tags = ['Motorista']
    permission_classes = [TokenMatchesOASRequirements, UserIsDriver]
    required_alternate_scopes = {
        "GET": [["trips:driver:read"]],
        "PATCH": [["trips:driver:write"]],
        "DELETE": [["trips:driver:write"]]
    }

    def get_queryset(self):
        # Só pode editar caronas que ainda não aconteceram
        if self.request.method != 'GET' and Trip.objects.get(pk=self.kwargs['trip_id']).datetime <= timezone.now():
            return Passenger.objects.none()
        return super().get_queryset().filter(trip=self.kwargs['trip_id'])

    def get_serializer_class(self):
        if self.request.method == 'PATCH':
            return DriverActionsSerializer
        return super().get_serializer_class()

    def get_object(self):
        """Get passenger from scoped user ID"""
        qs = self.get_queryset()
        lookup_url_kwarg = self.lookup_url_kwarg or self.lookup_field
        passenger_user_id = self.kwargs[lookup_url_kwarg]
        trip_id = self.kwargs['trip_id']
        app1 = self.request.auth.application
        try:
            # Get app and passenger user from the scoped user id
            app2, passenger = get_application_model().recover_scoped_user_id(passenger_user_id, True)
        except InvalidScopedUserId:
            return Response(status=status.HTTP_404_NOT_FOUND)
        if app1.id != app2.id:
            # Assert that the app from the scoped user id is the one from the token
            return Response(status=status.HTTP_404_NOT_FOUND)
        trip = Trip.objects.filter(id=trip_id, user=self.request.user).first()
        if trip is None:
            # Assert that the trip from the path parameter exists and belongs to the token owner
            return Response(status=status.HTTP_404_NOT_FOUND)
        if trip.check_is_passenger(passenger, raise_on_error=False) is None:
            # Assert that the passenger belongs to the trip
            return Response(status=status.HTTP_404_NOT_FOUND)
        user = get_object_or_404(qs, user=passenger)
        return user

    @swagger_auto_schema(
        responses={
            400: "Seus parâmetros GET estão mal formatados",
            404: "Carona pesquisada não existe ou você não tem acesso"
        },
        manual_parameters=[
            openapi.Parameter(DriverTripListRetrieveSerializer.include_arg_name, openapi.IN_QUERY,
                              "Seleciona dados retornados, separados por vírgula. Campos aninhados são suportados. Exemplo: `fields=campo1,campo2{sub_campo1, sub_campo2}`", type=openapi.TYPE_STRING),
            openapi.Parameter(DriverTripListRetrieveSerializer.exclude_arg_name, openapi.IN_QUERY,
                              "Exclui dados retornados, separados por vírgula. Campos aninhados são suportados. Exemplo: `exclude=campo1,campo2{sub_campo1, sub_campo2}`", type=openapi.TYPE_STRING)
        ],
        security=[
            {'unicaronas auth': ['trips:driver:read']}
        ]
    )
    def retrieve(self, *args, **kwargs):
        """Detalhar passageiro

        Permite acessar os dados detalhados de um passageiro de uma carona do usuário.

        Para acessar, use a ID de uma carona(`trip_id`) que o usuário é motorista e a ID do passageiro(`passenger_user_id`)

        > **Dica:** Você também pode usar os parâmetros GET `fields` e `exclude` para filtrar os campos retornados pela API
        """
        return super().retrieve(*args, **kwargs)

    @swagger_auto_schema(
        responses={
            400: "Seus parâmetros GET estão mal formatados",
        },
        manual_parameters=[
            openapi.Parameter('fields', openapi.IN_QUERY,
                              "Seleciona dados retornados, separados por vírgula. Campos aninhados são suportados. Exemplo: `fields=campo1,campo2{sub_campo1, sub_campo2}`", type=openapi.TYPE_STRING),
            openapi.Parameter('exclude', openapi.IN_QUERY,
                              "Exclui dados retornados, separados por vírgula. Campos aninhados são suportados. Exemplo: `exclude=campo1,campo2{sub_campo1, sub_campo2}`", type=openapi.TYPE_STRING)
        ],
        filter_inspectors=[DjangoFilterDescriptionInspector],
        security=[
            {'unicaronas auth': ['trips:driver:read']}
        ]
    )
    def list(self, *args, **kwargs):
        """Listar passageiros

        Permite listar os passageiros de uma carona que o usuário criou.

        Para acessar, use a ID de uma carona(`trip_id`) que o usuário é motorista

        > **Dica:** Você também pode usar os parâmetros GET `fields` e `exclude` para filtrar os campos retornados pela API
        """
        return super().list(*args, **kwargs)

    @swagger_auto_schema(
        responses={
            404: 'Passageiro não existe ou a carona já aconteceu'
        },
        security=[
            {'unicaronas auth': ['trips:driver:write']}
        ]
    )
    def destroy(self, *args, **kwargs):
        """Remover passageiro

        Para acessar, use a ID de uma carona(`trip_id`) que o usuário é motorista e a ID do passageiro(`passenger_user_id`)

        Permite remover passageiros de caronas que **ainda não aconteceram** e que o usuário criou. Caso a carona já tenha acontecido, a resposta desse endpoint será um erro *404*.
        """
        passenger = self.get_object()
        passenger.forfeit()
        return Response(status=status.HTTP_200_OK)

    @swagger_auto_schema(
        responses={
            404: 'Carona não existe, já aconteceu, ou você não tem permissão para acessá-la',
            400: 'A ação não é compatível com o estado do passageiro',
        },
        security=[
            {'unicaronas auth': ['trips:driver:write']}
        ]
    )
    def partial_update(self, *args, **kwargs):
        """Alterar o status de um passageiro

        Permite a alteração do status de um passageiro em caronas que **ainda não aconteceram**. Caso a carona já tenha acontecido, a resposta desse endpoint será um erro *404*.

        Para acessar, use a ID de uma carona(`trip_id`) que o usuário é motorista e a ID do passageiro(`passenger_user_id`)

        As ações são enviadas por um parâmetro no *PATCH* chamado `action` e têm os seguintes efeitos:

        | Ação          | Atua em                   | Efeito                        |
        | ------------- |---------------------------|-------------------------------|
        | `approve`     | Passageiros **pendentes**, **negados** ou **removidos** | Aprova passageiro             |
        | `deny`        | Passageiros **pendentes** | Nega passageiro               |
        | `forfeit`     | Passageiros **aprovados** | Remove um passageiro da carona|
        """
        return super().partial_update(*args, **kwargs)

    def perform_update(self, serializer):
        action = serializer.validated_data['action']
        passenger = serializer.instance
        trip = Trip.objects.get(id=self.kwargs['trip_id'])
        action_map = {
            'approve': trip.approve_passenger,
            'deny': trip.deny_passenger,
            'forfeit': trip.forfeit_passenger
        }
        try:
            action_map[action](passenger.user)
        except PassengerPendingError:
            raise ValidationError({'detail': 'Operação inválida para passageiros pendentes'}, code=status.HTTP_400_BAD_REQUEST)
        except PassengerApprovedError:
            raise ValidationError({'detail': 'Operação inválida para passageiros aprovados'}, code=status.HTTP_400_BAD_REQUEST)
        except PassengerDeniedError:
            raise ValidationError({'detail': 'Operação inválida para passageiros negados ou removidos'}, code=status.HTTP_400_BAD_REQUEST)
        except TripFullError:
            raise ValidationError({'detail': 'Carona já está cheia'}, code=status.HTTP_400_BAD_REQUEST)
