from django.utils import timezone
from django.db.models import Count, F, Q
from rest_framework import viewsets, status
from rest_framework.exceptions import ValidationError
from rest_framework_filters.backends import RestFrameworkFilterBackend
from oauth2_provider.contrib.rest_framework.permissions import TokenMatchesOASRequirements
from drf_yasg.utils import swagger_auto_schema
from drf_yasg import openapi
from project.mixins import PrefetchQuerysetModelMixin, PatchModelMixin
from ..inspectors import DjangoFilterDescriptionInspector
from ..filters import TripFilterSet, LocalizedOrderingFilter
from ..serializers import SearchTripSerializer, FuturePassengerActionsSerializer
from .....models import Trip
from .....exceptions import TripFullError, PassengerBookedError


class SearchTripViewset(
        PrefetchQuerysetModelMixin,
        PatchModelMixin,
        viewsets.ReadOnlyModelViewSet):
    """Viagens

    """
    # Only allow trips in the future
    swagger_tags = ['Pesquisa Interna']
    queryset = Trip.objects.all()
    max_limit = 50
    limit = 10
    filter_backends = (
        RestFrameworkFilterBackend,
        LocalizedOrderingFilter,
    )
    filter_class = TripFilterSet
    ordering_fields = [
        'datetime', 'price'
    ]
    ordering = ['datetime', 'price']
    serializer_class = SearchTripSerializer
    permission_classes = [TokenMatchesOASRequirements]
    required_alternate_scopes = {
        "GET": [["trips:read"]],
        "PATCH": [["trips:passenger:write"]],
    }

    def get_queryset(self):
        qs = super().get_queryset()
        qs = qs.exclude(passengers__user__in=[self.request.user])
        qs = qs.exclude(user=self.request.user)
        seats_left = F('max_seats') - Count(
            'passengers',
            filter=~Q(passengers__status="denied")
        )
        qs = qs.annotate(seats_left=seats_left)
        qs = qs.filter(seats_left__gt=0)
        qs = qs.filter(datetime__gt=timezone.now())
        return qs

    def get_serializer_class(self):
        if self.request.method == 'PATCH':
            return FuturePassengerActionsSerializer
        return super().get_serializer_class()

    @swagger_auto_schema(
        responses={
            400: "Seus parâmetros GET estão mal formatados",
            404: "Carona pesquisada não existe"
        },
        manual_parameters=[
            openapi.Parameter('fields', openapi.IN_QUERY,
                              "Seleciona dados retornados. Lista separada por vírgula dos campos a serem retornados. Campos aninhados são suportados. Exemplo: `fields=campo1,campo2{sub_campo1, sub_campo2}`", type=openapi.TYPE_STRING),
            openapi.Parameter('exclude', openapi.IN_QUERY,
                              "Exclui dados retornados. Lista separada por vírgula dos campos a serem excluídos. Campos aninhados são suportados. Exemplo: `exclude=campo1,campo2{sub_campo1, sub_campo2}`", type=openapi.TYPE_STRING)
        ],
        security=[
            {'unicaronas auth': ['trips:read']}
        ]
    )
    def retrieve(self, *args, **kwargs):
        """Detalhes de uma carona

        Permite acessar detalhes de caronas **que ainda não aconteceram**, que **não estão cheias** e que o **usuário não é passageiro ou motorista**.
        > **Obs:** Só é acessível para caronas que ainda não aconteceram e que não estão cheias

        Para acessar, use a ID de uma carona pesquisada.

        > **Dica:** Você também pode usar os parâmetros GET `fields` e `exclude` para filtrar os campos retornados pela API
        """
        return super().retrieve(*args, **kwargs)

    @swagger_auto_schema(
        responses={
            400: "Seus parâmetros GET estão mal formatados",
            # 200: PaginatedResponseSerializer
        },
        manual_parameters=[
            openapi.Parameter('fields', openapi.IN_QUERY,
                              "Seleciona dados retornados. Lista separada por vírgula dos campos a serem retornados. Campos aninhados são suportados. Exemplo: `fields=campo1,campo2{sub_campo1, sub_campo2}`", type=openapi.TYPE_STRING),
            openapi.Parameter('exclude', openapi.IN_QUERY,
                              "Exclui dados retornados. Lista separada por vírgula dos campos a serem excluídos. Campos aninhados são suportados. Exemplo: `exclude=campo1,campo2{sub_campo1, sub_campo2}`", type=openapi.TYPE_STRING)
        ],
        filter_inspectors=[DjangoFilterDescriptionInspector],
        security=[
            {'unicaronas auth': ['trips:read']}
        ]
    )
    def list(self, *args, **kwargs):
        """Pesquisar caronas

        Permite fazer pesquisas de caronas **que ainda não aconteceram**, que **não estão cheias** e que o **usuário não é passageiro ou motorista** usando uma série de filtros *GET*.

        > **Atenção:** A intenção desse endpoint é permitir pesquisas para passageiros entrarem em caronas, mas ele pode ser usado por qualquer usuário.

        A API irá calcular as coordenadas origem e destino automaticamente usando a [API de Geocoding do Google](https://developers.google.com/maps/documentation/geocoding/intro).
        Por conta disso, o fornecimento de endereços incorretos poderá resultar em endereços que estarão completamente errados, como em outras cidades ou estados.

        O Unicaronas tenta mitigar isso mapeando endereços digitados com frequência e fazendo correção gramatical dos dados de entrada, mas nem sempre isso será suficiente para corrigir entradas ruins. Dessa forma, garanta que os resultados gerados são os esperados enviando endereços o mais completos possível.
        Gerar endereços completos é difícil, então considere as seguintes opções:
        - Dê opções limitadas de busca aos seus usários. Opções essas cujos endereços completos sejam conhecidos por você. Ex: Unicamp, Posto da 1, Metro Tietê, etc
        - Use uma API como a de [Autocomplete](https://developers.google.com/places/web-service/autocomplete) para gerar endereços completos enquanto o usuário digita

        Os resultados da pesquisa por destino e origem sempre são limitados ao raio de pesquisa escolhido com `origin_radius` e `destination_radius`. Esses valores têm máximos e mínimos:

        |Parâmetro|Padrão|Mínimo|Máximo|
        | ---|---|---|---|
        |`origin_radius`|5 km|0.05 km|10 km|
        |`destination_radius`|5 km|0.05 km|20 km|

        Alguns parâmetros *GET* são obrigatórios:

        | Parâmetros obrigatórios|
        | --------------|
        | `origin`|
        | `destination`|

        > **Dica:** Você também pode usar os parâmetros GET `fields` e `exclude` para filtrar os campos retornados pela API
        """
        required_fields = [
            'origin',
            'destination'
        ]

        for field in required_fields:
            if not self.request.query_params.get(field, False):
                raise ValidationError(f'Parâmetro GET `{field}` faltando', code=status.HTTP_400_BAD_REQUEST)
        return super().list(*args, **kwargs)

    @swagger_auto_schema(
        responses={
            404: 'Carona não existe, já aconteceu, ou você não tem permissão para acessá-la',
            400: 'A ação não é compatível com o estado do passageiro',
        },
        security=[
            {'unicaronas auth': ['trips:passenger:write']}
        ]
    )
    def partial_update(self, *args, **kwargs):
        """Agendar carona

        Permite que usuários se tornem passageiros de uma carona que **que ainda não aconteceram**, que **não estão cheias** e que o **usuário não é passageiro ou motorista**.

        > **Atenção:** O status inicial do passageiro na carona depende do parâmetro `auto_approve` na carona. Caso ele seja `true`, o passageiro será aceito assim que submeter o pedido. Caso seja `false`, o motorista terá que aceitar o passageiro.

        Para acessar, use a ID de uma carona pesquisada.

        As ações são enviadas por um parâmetro no *PATCH* chamado `action` e têm os seguintes efeitos:

        | Ação          | Efeito                        |
        | ------------- |-------------------------------|
        | `book`     |Usuário entra para a fila de passageiros na carona|
        """
        return super().partial_update(*args, **kwargs)

    def perform_update(self, serializer):
        action = serializer.validated_data['action']

        trip = serializer.instance
        action_map = {
            'book': trip.book_user,
        }
        try:
            action_map[action](self.request.user)
        except TripFullError:
            raise ValidationError({'detail': 'Carona já está cheia'}, code=status.HTTP_400_BAD_REQUEST)
        except PassengerBookedError:
            raise ValidationError({'detail': 'Usuário já é passageiro da carona'}, code=status.HTTP_400_BAD_REQUEST)
