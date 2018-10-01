import re
from rest_framework.views import APIView
from rest_framework.response import Response
from drf_yasg.utils import swagger_auto_schema
from third_parties.pipeline import Pipeline
from third_parties.serializers import ResultSerializer
from ..serializers import ThirdPartyQuerySerializer


class ThirdPartyTripSearchView(APIView):
    swagger_tags = ['Pesquisa Externa']
    serializer_class = ThirdPartyQuerySerializer

    @swagger_auto_schema(
        query_serializer=ThirdPartyQuerySerializer,
        responses={
            400: 'Seus parâmetros GET estão mal formatados',
            200: ResultSerializer
        }
    )
    def get(self, request, format=None):
        """Pesquisar caronas externas

        Permite a pesquisa de caronas em bancos de dados externos
        ao Unicaronas.

        Os dados retornados por esse endpoint são bem mais limitados
        que os dados retornados pelo endpoint de caronas internas e não
        há controle sobre as pessoas oferecendo as caronas nesses serviços externos.

        > **Sugestão:** Só mostre resultados desse endpoint aos seus usuários
        se não forem encontradas caronas pelo endpoint de caronas internas.

        As fontes de caronas acessíveis por esse endpoint são:

        |Fonte|Descrição|Observação|
        | ---|---|---|
        |`facebook`|Grupos no Facebook de caronas na Unicamp|Apenas membros dos grupos podem visualizar suas caronas|
        |`blablacar`|API do [BlaBlaCar](https://blablacar.com.br)|BlaBlaCar é um serviço pago|
        """
        query_serializer = self.serializer_class(data=request.query_params)
        query_serializer.is_valid(raise_exception=True)
        query_data = query_serializer.validated_data
        query_data['request'] = request
        sources = re.split(', ', query_data.pop('sources', 'all'))
        pipe = Pipeline(sources)
        results = pipe.search(**query_data)
        return Response(data=results.validated_data)
