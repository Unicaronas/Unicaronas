from django.utils import timezone
from django.db.models import Q
from rest_framework import viewsets
from drf_yasg.utils import swagger_auto_schema
from drf_yasg import openapi
from project.mixins import PrefetchQuerysetModelMixin
from project.filters import LocalizedOrderingFilter
from oauth2_provider.contrib.rest_framework.permissions import TokenMatchesOASRequirements
from .serializers import AlarmCreateSerializer, AlarmListRetrieveSerializer
from ....models import Alarm


class AlarmViewset(
        PrefetchQuerysetModelMixin,
        viewsets.ModelViewSet):

    swagger_tags = ['Alarmes']
    lookup_field = 'id'
    serializer_class = AlarmCreateSerializer
    queryset = Alarm.objects.all()
    max_limit = 50
    limit = 10
    filter_backends = (
        LocalizedOrderingFilter,
    )
    ordering_fields = [
        'datetime_gte', 'datetime_lte'
    ]
    ordering = ['datetime_gte']
    permission_classes = [TokenMatchesOASRequirements]
    required_alternate_scopes = {
        "GET": [["alarms:read"]],
        "POST": [["alarms:write"]],
        "PUT": [["alarms:write"]],
        "PATCH": [["alarms:write"]],
        "DELETE": [["alarms:write"]]
    }

    def get_queryset(self):
        qs = super().get_queryset()
        # Only allow editing and viewing the user's alarms
        qs = qs.filter(user=self.request.user)
        # Only list alarms that didn't happen
        qs = qs.filter(Q(datetime_lte__isnull=True) | Q(datetime_lte__gte=timezone.now()))
        return qs

    def get_serializer_class(self):
        if self.request.method == 'GET':
            return AlarmListRetrieveSerializer
        return AlarmCreateSerializer

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
            {'OAuth2': ['alarms:read']}
        ]
    )
    def retrieve(self, *args, **kwargs):
        """Detalhes de um alarme

        Permite acessar detalhes de alarmes **que ainda não aconteceram** e que pertencem ao usuário.

        Para acessar, use a ID de um alarme pesquisado.

        > **Dica:** Você também pode usar os parâmetros GET `fields` e `exclude` para filtrar os campos retornados pela API
        """
        return super().retrieve(*args, **kwargs)

    @swagger_auto_schema(
        responses={
            400: "Seus parâmetros GET estão mal formatados",
        },
        manual_parameters=[
            openapi.Parameter('fields', openapi.IN_QUERY,
                              "Seleciona dados retornados. Lista separada por vírgula dos campos a serem retornados. Campos aninhados são suportados. Exemplo: `fields=campo1,campo2{sub_campo1, sub_campo2}`", type=openapi.TYPE_STRING),
            openapi.Parameter('exclude', openapi.IN_QUERY,
                              "Exclui dados retornados. Lista separada por vírgula dos campos a serem excluídos. Campos aninhados são suportados. Exemplo: `exclude=campo1,campo2{sub_campo1, sub_campo2}`", type=openapi.TYPE_STRING)
        ],
        security=[
            {'OAuth2': ['alarms:read']}
        ]
    )
    def list(self, *args, **kwargs):
        """Listar alarmes

        Permite listar alarmes **que ainda não aconteceram** e que pertencem ao usuário.

        > **Dica:** Você também pode usar os parâmetros GET `fields` e `exclude` para filtrar os campos retornados pela API
        """
        return super().list(*args, **kwargs)

    @swagger_auto_schema(
        responses={
            201: AlarmCreateSerializer,
            400: 'Dados do pedido contém erros'
        },
        security=[
            {'OAuth2': ['alarms:write']}
        ]
    )
    def create(self, request, *args, **kwargs):
        """Criar alarme

        Crie alarmes pelo usuário.

        A API irá gerar automaticamente os dados faltantes de origem e destino usando a [API de Geocoding do Google](https://developers.google.com/maps/documentation/geocoding/intro).
        Por conta disso, o fornecimento de endereços incorretos poderá resultar em endereços que estarão completamente errados, como em outras cidades ou estados.

        O Unicaronas tenta mitigar isso mapeando endereços digitados com frequência e fazendo correção gramatical dos dados de entrada, mas nem sempre isso será suficiente para corrigir entradas ruins. Dessa forma, garanta que os resultados gerados são os esperados enviando endereços o mais completos possível.
        Gerar endereços completos é difícil, então considere as seguintes opções:
        - Dê opções limitadas de busca aos seus usários. Opções essas cujos endereços completos sejam conhecidos por você. Ex: Unicamp, Posto da 1, Metro Tietê, etc
        - Use uma API como a de [Autocomplete](https://developers.google.com/places/web-service/autocomplete) para gerar endereços completos enquanto o usuário digita

        Nem todos os parâmetros são obrigatórios. Na falta deles, esses serão os padrões:

        | Campo                | Padrão        |
        | ---------------------|---------------|
        | `origin_radius`      | 5             |
        | `destination_radius` | 5             |

        > Parámetros não listados acima e que não são obrigatórios não serão usados para filtrar caronas criadas.
        """
        return super().create(request, *args, **kwargs)

    @swagger_auto_schema(
        responses={
            200: AlarmListRetrieveSerializer,
            404: 'Alarme não existe, já aconteceu, ou você não tem permissão para acessá-lo',
            400: 'Dados do pedido contém erros',
        },
        security=[
            {'OAuth2': ['alarms:write']}
        ]
    )
    def update(self, request, *args, **kwargs):
        """Atualizar alarme

        Permite a alteração de dados de alarmes que **ainda não aconteceram**. Caso o alarme já tenha acontecido, a resposta desse endpoint será um erro *404*.
        """
        return super().update(request, *args, **kwargs)

    @swagger_auto_schema(
        responses={
            200: AlarmListRetrieveSerializer,
            400: 'Dados do pedido contém erros',
            404: 'Alarme não existe, já aconteceu, ou você não tem permissão para acessá-lo',
        },
        security=[
            {'OAuth2': ['alarms:write']}
        ]
    )
    def partial_update(self, *args, **kwargs):
        """Atualizar parcialmente alarme

        Permite a alteração de dados de alarmes que **ainda não aconteceram**. Caso o alarme já tenha acontecido, a resposta desse endpoint será um erro *404*.
        """
        return super().partial_update(*args, **kwargs)

    @swagger_auto_schema(
        responses={
            404: 'Alarme não existe, já aconteceu, ou você não tem permissão para acessá-lo',
        },
        security=[
            {'OAuth2': ['alarms:write']}
        ]
    )
    def destroy(self, *args, **kwargs):
        """Apagar alarme

        Permite apagar alarmes que **ainda não aconteceram**. Caso o alarme já tenha acontecido, a resposta desse endpoint será um erro *404*.
        """
        return super().destroy(*args, **kwargs)
