from django.urls import path, include
from django.conf import settings
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
## Bem-vind@ à API REST do Unicaronas!


# O que é o Unicaronas?
O [Unicaronas](https://unicaronas.com) é um serviço gratuito de caronas, exclusivo para estudantes universitários, gerido independentemente por estudantes da Unicamp. A principal característica do Unicaronas é que, oficialmente, tudo que ele oferece é essa API. Todas as interfaces e aplicativos foram criados por estudantes membros da comunidade que usam nossa API para servir seus usuários.

Criamos o Unicaronas pois percebemos que pegar caronas é uma parte essencial da vida de boa parte dos estudantes universitários, que voltam periodicamente para suas cidades de origem. Assim como o Unicaronas, outros serviços similares existem, como o [BlaBlaCar](https://blablacar.com) e grupos de caronas no Facebook. Infelizmente nem sempre esses outros serviços suprem as necessidades particulares de nós, estudantes.

Dessa forma, para suprir a demanda de um serviço de caronas seguro e gratuito para universitários, nasceu o Unicaronas!

# Antes de começar
Para começar a usar e fazer chamadas para a API, é necessário que você [crie sua conta](/accounts/signup/) em nosso serviço e depois [crie um aplicativo](/applications/create/).
> **Obs**: Apenas estudantes universitários serão capazes de criar uma conta

Durante a criação do seu aplicativo, você terá que responder um formulário com várias opções que serão usadas para configurar seu acesso [OAuth2](https://oauth.net/2/). Se você não sabe o que é OAuth2 ou precisa de ajuda para escolher as opções corretas, leia [nosso guia](/what_is_oauth/) que explica os principais conceitos e o significado de cada opção disponível na tela de criação do seu aplicativo.

Com o seu aplicativo criado, você terá uma ou duas chaves (`client_id` e `client_secret`) que serão sua forma de autenticação na API.

# Introdução à API
A API do Unicaronas é separada em blocos lógicos que representam cada modelo interno do serviço.

Todos os pedidos à API são protegidos por OAuth2 e, por isso, devem ser acompanhados de um token de acesso que represente um usuário do serviço. Todos os seus chamados serão feitos em nome do usuário que te deu acesso ao token, portanto nunca execute ações sem o consentimento deste e prefira realizar ações de escrita apenas em resposta a ações diretas do usuário.

Para acessar os endpoints da API o seu token de acesso deverá portar as permissões necessárias para tal. Você pode ver detalhes sobre cada permissão disponível na [seção de autenticação](#section/Authentication) e poderá ver quais permissões cada endpoint requer no parâmetro *authorizations* listado na descrição destes.

# Limites de pedidos
Para garantir a disponibilidade da API para todos, alguns limites são aplicados. Em particular, as chamadas são limitadas em duas categorias: `burst`, chamadas rápidas em um minuto, e `sustained`, chamadas totais feitas no dia.

| Categoria     | Limite        |
| ------------- |---------------|
| `burst`       | 60/min        |
| `sustained`   | 10.000/dia    |

> **Nota:** Esses limites são aplicados por aplicativo, ou seja, cada aplicativo é limitado independentemente.

Os limites são aplicados ao mesmo tempo, de forma que se você superar 60 pedidos em um minuto, ficará o restante do minuto sem poder fazer chamadas adicionais. Ao mesmo tempo, se você fizer mais que 10.000 chamadas em um dia, ficará sem acesso pelo resto deste.

# Webhooks
O Unicaronas também oferece [webhooks](https://www.chargebee.com/blog/what-are-webhooks-explained/) como um serviço opcional externo à API que pode ser útil para você.

Nossos webhooks são enviados automaticamente como pedidos **POST** em resposta a alguns eventos dos usuários. Para recebê-los, seu aplicativo terá que ter uma *URI válida* definida em suas configurações e ter as *permissões corretas em tokens não expirados* fornecidos pelo usuário.

Todos os webhooks são enviados como *JSON* e contém o seguinte objeto em seu corpo:
```json
{
    "event": "<event-type>",
    "payload": {
        <event-payload-object>
    }
}
```
- `event` contém o tipo do evento. Use essa informação para decidir o que fazer com o `payload`
- `payload` contém o objeto do evento. Ele sempre inclui o `user_id` do usuário para quem o evento se aplica.

## Pra que usar webhooks?
Webhooks são a melhor maneira de agir em resposta a eventos na API. O que você fará com esses eventos é decisão sua, mas alguns exemplos são:
- Enviar notificações *push* para seus usuários, os motivando a responderem à ação usando seu aplicativo
- Atualizar informações sobre o usuário em seu banco de dados

Abaixo está a lista de webhooks disponíveis com seus eventos ativadores e o conteúdo de seu `payload`:

## Webhooks para passageiros
|Evento|Detalhes|Permissão necessária|
|--|--|--|--|--|
|`passenger_pending`|Seu usuário está pendente em uma carona|`trips:passenger:read`|
|`passenger_approved`|Seu usuário foi aprovado em uma carona|`trips:passenger:read`|
|`passenger_denied`|Seu usuário foi negado em uma carona pelo motorista|`trips:passenger:read`|
|`passenger_forfeit`|Seu usuário foi removido de uma carona pelo motorista|`trips:passenger:read`|
|`trip_deleted`|Uma viagem em que seu usuário era passageiro foi apagada pelo motorista|`trips:passenger:read`|

### Formato de `passenger_pending`:
```json
{
    "event": "passenger_pending",
    "payload": {
        "user_id": "abc123",                                // ID de usuário do passageiro (seu usuário)
        "trip_id": "42",                                    // ID da carona
        "resource_url": "https://unicaronas.com/api/..."    // URL da carona no endpoint Passageiro -> Detalhes de uma carona
    }
}
```
### Formato de `passenger_approved`:
```json
{
    "event": "passenger_approved",
    "payload": {
        "user_id": "abc123",                                // ID de usuário do passageiro (seu usuário)
        "trip_id": "42",                                    // ID da carona
        "resource_url": "https://unicaronas.com/api/..."    // URL da carona no endpoint Passageiro -> Detalhes de uma carona
    }
}
```
### Formato de `passenger_denied`:
```json
{
    "event": "passenger_denied",
    "payload": {
        "user_id": "abc123",                                // ID de usuário do passageiro (seu usuário)
        "trip_id": "42",                                    // ID da carona
        "resource_url": "https://unicaronas.com/api/..."    // URL da carona no endpoint Passageiro -> Detalhes de uma carona
    }
}
```
### Formato de `passenger_forfeit`:
```json
{
    "event": "passenger_forfeit",
    "payload": {
        "user_id": "abc123",                                // ID de usuário do passageiro (seu usuário)
        "trip_id": "42",                                    // ID da carona
        "resource_url": "https://unicaronas.com/api/..."    // URL da carona no endpoint Passageiro -> Detalhes de uma carona
    }
}
```
### Formato de `trip_deleted`:
```json
{
    "event": "trip_deleted",
    "payload": {
        "user_id": "abc123",                // ID de usuário do passageiro (seu usuário)
        "origin": "Rua abc, 123",           // Endereço de origem da carona
        "destination": "Rua abc, 123",      // Endereço de origem da carona
        "datetime": "2018-10-21T09:24:10"   // Datetime da carona
    }
}
```
## Webhooks para motoristas
|Evento|Detalhes|Permissão necessária|
|--|--|--|--|--|
|`driver_passenger_pending`|Um passageiro está pendente em uma carona do seu usuário|`trips:driver:read`|
|`driver_passenger_approved`|Um passageiro foi aprovado em uma carona do seu usuário|`trips:driver:read`|
|`driver_passenger_give_up`|Um passageiro em uma carona do seu usuário desistiu da viagem|`trips:driver:read`|

### Formato de `driver_passenger_pending`:
```json
{
    "event": "driver_passenger_pending",
    "payload": {
        "user_id": "abc123",                                // ID de usuário do motorista (seu usuário)
    "trip_id": "42",                                        // ID da carona
        "resource_url": "https://unicaronas.com/api/..."    // URL do passageiro no endpoint Motorista -> Detalhar passageiro
    }
}
```
### Formato de `driver_passenger_approved`:
```json
{
    "event": "driver_passenger_approved",
    "payload": {
        "user_id": "abc123",                                // ID de usuário do motorista (seu usuário)
        "trip_id": "42",                                    // ID da carona
        "resource_url": "https://unicaronas.com/api/..."    // URL do passageiro no endpoint Motorista -> Detalhar passageiro
    }
}
```
### Formato de `driver_passenger_give_up`:
```json
{
    "event": "driver_passenger_give_up",
    "payload": {
        "user_id": "abc123",                                // ID de usuário do motorista (seu usuário)
        "trip_id": "42",                                    // ID da carona
        "passenger": {
            "first_name": "Fulano",                         // Primeiro nome do passageiro
            "last_name": "de Tal"                           // Sobrenome do passageiro
        },
        "resource_url": "https://unicaronas.com/api/..."    // URL da carona no endpoint Motorista -> Detalhar carona
    }
}
```
## Webhooks para alarmes
|Evento|Detalhes|Permissão necessária|
|--|--|--|--|--|
|`alarm_dispatched`|Uma carona compatível com um alarme do seu usuário foi criada|`trips:read`|

### Formato de `alarm_dispatched`:
```json
{
    "event": "alarm_dispatched",
    "payload": {
        "user_id": "abc123",                                // ID de usuário do seu usuário
        "trip_id": "42",                                    // ID da carona encontrada
        "resource_url": "https://unicaronas.com/api/..."    // URL da carona no endpoint Pesquisa Interna -> Detalhes de uma carona
    }
}
```

# FAQ
## Quem pode usar a API?
Apenas estudantes universitários cadastrados no Unicaronas podem criar aplicativos e utilizar a API.

## Como eu me cadastro?
Para se cadastrar, basta preencher [esse formulário](/accounts/signup/)

## Como eu crio aplicativos?
Para criar aplicativos, basta preencher o [formulário de aplicativos](/applications/create/)

## Recebi o erro As credenciais de autenticação não foram fornecidas. O que significa?
Você está recebendo esse erro pois não incluiu seu token de acesso como *Header* do pedido.
 Seu token de acesso deve ser incluído como um *Header* no formato *Authorization: Bearer `<seu-token>`

Caso você tenha certeza que está enviando seu token no *Header* mas o erro `As credenciais de autenticação não foram fornecidas.` continuar aparecendo, quer dizer que seu token é inválido ou já expirou. Lembre-se que os tokens têm validade de apenas 1 hora.

## Recebi o erro Você não tem permissão para executar essa ação. O que significa?
Esse erro significa que seu token é válido, mas não possui os `scopes` necessários para acessar o endpoint. Para a lista de `scopes` necessários para cada endpoint, procure pela seção *AUTHORIZATIONS* em cada endpoint.

## Recebi o erro Too Many Requests. O que significa?
Significa que você ultrapassou as cotas da API e seu acesso foi cortado temporariamente. Leia sobre [os limites da API](#section/Limites-de-pedidos) para detalhes.

## Cadastrei um Webhook, mas não estou recebendo eventos!
Para receber os eventos por webhooks, certifique-se de que:
- A URL do seu webhook está correta e é acessível pela internet
- Seu aplicativo contém pelo menos um token do seu usuário-alvo com as permissões necessárias

Se você continuar sem receber webhooks de um usuário em particular, significa que esse usuário declarou que não deseja receber avisos de aplicativos
""".replace('https://unicaronas.com', settings.ROOT_URL).replace('http://unicaronas.com', settings.ROOT_URL),
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
