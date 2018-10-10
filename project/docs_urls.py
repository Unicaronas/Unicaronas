from django.urls import path, include
from rest_framework import permissions
from drf_yasg.views import get_schema_view
from drf_yasg import openapi
from . import api_urls
from .swagger_schema import TaggedDescriptionSchemaGenerator
from .utils import get_current_version

schema_view = get_schema_view(
    openapi.Info(
        title="Unicaronas API",
        default_version=get_current_version(),
        description="""
Texto inicial

# O que é o Unicaronas?

# Antes de começar

# Introdução à API

# Limites de pedidos
Para garantir a disponibilidade da API para todos, alguns limites são aplicados. Em particular, as chamadas são limitadas em duas categorias: `burst`, chamadas rápidas em um minuto, e `sustained`, chamadas totais feitas no dia.

| Categoria     | Limite        |
| ------------- |---------------|
| `burst`       | 60/min        |
| `sustained`   | 10.000/dia    |

> **Nota:** Esses limites são aplicados por aplicativo, ou seja, cada aplicativo é limitado independentemente.

Os limites são aplicados ao mesmo tempo, de forma que se você superar 60 pedidos em um minuto, ficará o restante do minuto sem poder fazer chamadas adicionais. Ao mesmo tempo, se você fizer mais que 10.000 chamadas em um dia, ficará sem acesso pelo resto deste.

# Melhores práticas

# Como fazer pedidos

## Exemplos

### Python
```Python
Código em python com requests
```

### Javascript
```Javascript
Código em javascript com fetch
```

# FAQ

# Criando aplicativos
""",
        terms_of_service="https://unicaronas.com/terms_and_conditions/",
        contact=openapi.Contact(
            name="Suporte", email="contato@unicaronas.com", url="https://unicaronas.com"),
        license=openapi.License(
            name="AGPL3", url="https://opensource.org/licenses/AGPL-3.0"),
        x_logo={
            "url": "/static/project/img/social/og-image.jpg",
            "backgroundColor": "#FFFFFF"
        }
    ),
    # validators=['flex', 'ssv'],
    public=True,
    permission_classes=(permissions.AllowAny,),
    patterns=[path('api/', include(api_urls))],
    generator_class=TaggedDescriptionSchemaGenerator
)

app_name = 'docs'


docs_urlpatterns = [
    path('swagger<str:format>', schema_view.without_ui(
        cache_timeout=0), name='schema-json'),
    path('swagger/', schema_view.with_ui('swagger',
                                         cache_timeout=0), name='schema-swagger-ui'),
    path('', schema_view.with_ui('redoc',
                                 cache_timeout=0), name='schema-redoc'),
]


urlpatterns = [
    path('v1.0/', include((docs_urlpatterns, 'docs'), namespace='v1.0')),
]
