from rest_framework import viewsets
from rest_framework_filters.backends import RestFrameworkFilterBackend
from drf_yasg.utils import swagger_auto_schema
from drf_yasg import openapi
from project.serializers import ExceptionSerializer
from project.mixins import PrefetchQuerysetModelMixin
from .inspectors import DjangoFilterDescriptionInspector
from .filters import TripFilterSet, LocalizedOrderingFilter
from .serializers import TripListRetrieveSerializer, TripCreateUpdateSerializer
from .....models import Trip


class TripViewset(
        PrefetchQuerysetModelMixin,
        viewsets.ModelViewSet):
    """Viagens

    teste
    """
    queryset = Trip.objects.all()
    max_limit = 50
    limit = 1
    filter_backends = (
        RestFrameworkFilterBackend,
        LocalizedOrderingFilter,
    )
    filter_class = TripFilterSet
    ordering_fields = [
        'price', 'datetime'
    ]
    ordering = ['datetime', 'price']

    def get_queryset(self):
        qs = super().get_queryset()
        if self.request.method == 'GET':
            return qs
        else:
            # If is not a get request, limit results to the trips owned by the user
            return qs.filter(user=self.request.user)

    def get_serializer_class(self):
        if self.request.method == 'GET':
            return TripListRetrieveSerializer
        return TripCreateUpdateSerializer

    @swagger_auto_schema(
        responses={
            400: "Seus parâmetros GET estão mal formatados",
            403: ExceptionSerializer,
            404: "Carona pesquisada não existe"
        },
        manual_parameters=[
            openapi.Parameter(TripListRetrieveSerializer.include_arg_name, openapi.IN_QUERY,
                              "Seleciona dados retornados. Lista separada por vírgula dos campos a serem retornados. Campos aninhados são suportados. Exemplo: `" + TripListRetrieveSerializer.include_arg_name + "=`campo1,campo2{sub_campo1, sub_campo2}`", type=openapi.TYPE_STRING),
            openapi.Parameter(TripListRetrieveSerializer.exclude_arg_name, openapi.IN_QUERY,
                              "Exclui dados retornados. Lista separada por vírgula dos campos a serem excluídos. Campos aninhados são suportados. Exemplo: `" + TripListRetrieveSerializer.exclude_arg_name + "=`campo1,campo2{sub_campo1, sub_campo2}`", type=openapi.TYPE_STRING)
        ]
    )
    def retrieve(self, *args, **kwargs):
        """Detalhe de uma viagem

        Essa tela faz isso
        > Exemplo: aaaaa
        """
        return super().retrieve(*args, **kwargs)

    @swagger_auto_schema(
        responses={
            400: "Seus parâmetros GET estão mal formatados",
            403: ExceptionSerializer
        },
        manual_parameters=[
            openapi.Parameter(TripListRetrieveSerializer.include_arg_name, openapi.IN_QUERY,
                              "Seleciona dados retornados, separados por vírgula. Campos aninhados são suportados. Exemplo: `" + TripListRetrieveSerializer.include_arg_name + "=campo1,campo2{sub_campo1, sub_campo2}`", type=openapi.TYPE_STRING),
            openapi.Parameter(TripListRetrieveSerializer.exclude_arg_name, openapi.IN_QUERY,
                              "Exclui dados retornados, separados por vírgula. Campos aninhados são suportados. Exemplo: `" + TripListRetrieveSerializer.exclude_arg_name + "=campo1,campo2{sub_campo1, sub_campo2}`", type=openapi.TYPE_STRING)
        ],
        filter_inspectors=[DjangoFilterDescriptionInspector]
    )
    def list(self, *args, **kwargs):
        """Lista de viagens

        aaaa
        """
        return super().list(*args, **kwargs)

    @swagger_auto_schema(
        responses={
            201: TripListRetrieveSerializer,
        }
    )
    def create(self, *args, **kwargs):
        """Criar viagens

        Crie viagens pelo usuário

        Requer `trips:write`
        """
        return super().create(*args, **kwargs)

    @swagger_auto_schema(
        responses={
            200: TripListRetrieveSerializer,
        }
    )
    def update(self, *args, **kwargs):
        """Atualizar viagens

        Atualize viagens do usuário

        Requer `trips:write`
        """
        return super().update(*args, **kwargs)

    @swagger_auto_schema(
        responses={
            200: TripListRetrieveSerializer,
        }
    )
    def partial_update(self, *args, **kwargs):
        """Atualizar parcialmente viagens

        Atualize parcialmente as viagens do usuário

        Requer `trips:write`
        """
        return super().partial_update(*args, **kwargs)
