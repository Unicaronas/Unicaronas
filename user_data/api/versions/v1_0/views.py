from django.contrib.auth.models import User
from oauth2_provider.contrib.rest_framework.permissions import TokenMatchesOASRequirements
from drf_yasg.utils import swagger_auto_schema
from drf_yasg import openapi
from project.generics import PrefetchRetrieveAPIView
from .serializers import UserDataSerializer


class UserData(PrefetchRetrieveAPIView):
    """Usuário atual

    Um usuário é uma pessoa que autorizou seu aplicativo.
    Aqui é possível ler dados sobre o usuário dono do token usado para acessar esse endpoint.

    **Atenção:** A disponibilidade de certos dados depende das permissões(`scopes`) fornecidas pelo usuário durante a autorização. Para detalhes sobre quais permissões são requeridas por cada campo, leia sua descrição.
    > **Dica**: Prepare seu app de forma que a falta dos dados opcionais não quebre a experiência do usuário.
    """
    swagger_tags = ['Usuário']
    serializer_class = UserDataSerializer
    permission_classes = [TokenMatchesOASRequirements]
    queryset = User.objects.all()
    required_alternate_scopes = {
        "GET": [["basic:read"]],
    }
    field_permissions = {
        'basic:read': ['user_id', 'first_name', 'last_name'],
        'phone:read': ['profile'],
        'profile:read': ['profile'],
        'email:read': ['email', 'student'],
        'student:read': ['student'],
        'driver:read': ['driver'],
        'driver:preferences:read': ['driver'],
    }

    def get_object(self):
        return self.get_queryset().get(id=self.request.user.id)

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
        security=[
            {'OAuth2': [
                'basic:read',
                'phone:read',
                'profile:read',
                'email:read',
                'student:read',
                'driver:read',
                'driver:preferences:read'
            ]
            }
        ]
    )
    def get(self, *args, **kwargs):
        return super().get(*args, **kwargs)
