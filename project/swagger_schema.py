from collections import OrderedDict
from urllib.parse import urlencode, unquote_plus
from django.utils import timezone
from django.utils.crypto import get_random_string
from django.template.loader import render_to_string
from drf_yasg.inspectors.view import SwaggerAutoSchema, force_real_str
from drf_yasg.generators import OpenAPISchemaGenerator
from drf_yasg import openapi

tag_extra_data = {
    'Motorista': {
        'name': 'Motorista',
        'description': """
Nossa API de motoristas lhe permite construir serviços e soluções que tornam as vidas dos motoristas mais fáceis. Com a permissão do motorista, você consegue gerenciar caronas, passageiros e mais.

## Caronas
Ajude motoristas a gerenciar suas caronas, criando, listando e editando todas as viagens que decidirem fazer.

## Passageiros
Dê total controle aos seus motoristas sobre quem vai ou não em suas caronas. Gerencie aprovação e rejeição de passageiros e use os dados fornecidos para ajudar seus motoristas a fazerem viagens seguras e tranquilas.

> **Atenção:** Todos os endpoints dessa API só podem ser acessados caso seu usuário seja um *motorista*. Para saber se é motorista, o resultado do campo **driver** do endpoint [*Usuário Atual*](#operation/user_read) tem que ser diferente de `null`.
"""
    },
    'Passageiro': {
        'name': 'Passageiro',
        'description': """
Nossa API de passageiros lhe permite construir serviços e soluções que tornam as vidas dos passageiros mais fáceis. Com a permissão do motorista, você consegue gerenciar as caronas do seu usuário e executar ações nelas.

## Caronas
Ajude passageiros a entrar e sair de caronas, listar caronas passadas e futuras e muito mais.
"""
    },
    'Usuário': {
        'name': 'Usuário',
        'description': """
Veja os detalhes e informações do usuário que te deu permissão com a API de usuários.

## Dados e permissões
A API de usuário funciona sobre o usuário que autorizou seu aplicativo e te permite acessar os dados relacionados às permissões garantidas.

Os resultados da API de usuário se modificam dinamicamente de acordo com as permissões que o usuário te fornece, garantindo flexibilidade para você, que só terá que se preocupar com os dados que for usar, e privacidade ao usuário, que sempre vai saber que dados serão acessados por você.

> **Nota:** Por enquanto as únicas permissões que essa API garante são de *leitura* dos dados. Para que seu usuário altere seus dados, redirecione-o para o site principal do Unicaronas.
"""
    },
    'Pesquisa Interna': {
        'name': 'Pesquisa Interna',
        'description': """
A API de Pesquisas é o centro do Unicaronas. Com ela, você pode pesquisar nossa grande base de dados e colocar seus usuários nas melhores caronas possíveis.

## Pesquisas e caronas
Pesquise caronas usando uma poderosa variedade de filtros e garanta que seu usuário encontrará o que procura.
"""
    },
    'Pesquisa Externa': {
        'name': 'Pesquisa Externa',
        'description': """
API de pesquisas externas te leva além do banco de dados do Unicaronas. Com ela, você pode garantir que seu usuário sempre encontrará a carona que precisa.

## Bancos externos
A pesquisa externa difere da interna pois não usa caronas criadas no Unicaronas. Ela pesquisa por caronas em diversos grupos de Facebook e usa a API do BlaBlaCar para te fornecer um vasto leque de opções.

## Limitações
Por não usar caronas criadas pelo Unicaronas, não é possível verificar a identidade do motorista, nem coletar dados precisos da carona. Coisas como localização exata e número de assentos vagos não estarão disponíveis e, muitas vezes, as caronas podem ser para outros locais ou já estarem lotadas.

O Unicaronas usa diversas técnicas para mitigar esses erros e apresentar resultados de qualidade, mas não oferece nenhuma garantia de que os resultados são tão precisos quanto os resultados da pesquisa interna.

**Por esse motivo, considere expor caronas externas para seus usuários apenas quando não for possível encontrar caronas pela [pesquisa interna](#tag/Pesquisa-Interna) e quando criar [alarmes](#tag/Alarmes) não for possível.**
"""
    }, 'Alarmes': {
        'name': 'Alarmes',
        'description': """
Leia, edite e crie alarmes para o usuário que te deu permissão com a API de Alarmes.

## O que são alarmes?
Alarmes são a forma que seu usuário tem de ser notificado quando uma carona nova for criada em um horário específico.

Nem sempre o será possível encontrar caronas nos horários que mais precisamos. Em outros momentos nós sabemos com bastane antecedência, antes de qualquer motorista criar caronas, que precisaremos estar em um local em uma certa hora.
O Unicaronas tenta solucionar isso com a API de alarmes.

Com a API de alarmes é possível notificar usuários assim que essas caronas forem criadas, para que eles não tenham que realizar a pesquisa novamente e possam ser os primeiros a fazerem a reserva.

Sua API é bem semelhante à API de [pesquisa interna](#tag/Pesquisa-Interna) e permite que você *salve* uma pesquisa do seu usuário.
Sempre que uma carona nova for criada, o Unicaronas verificará se alguém criou um alarme que coincida com os parâmetros da carona nova. Se coincidir, o Unicaronas
enviará [Webhooks](#tag/Webhooks) para todos os aplicativos conectados ao usuário com informações sobre a nova carona.
"""
    }
}


class XCodeSampleAutoSchema(SwaggerAutoSchema):

    def process_string_parameter(self, parameter):
        min_length = getattr(parameter, 'minLength', 10)
        max_length = getattr(parameter, 'maxLength', 100)
        enum = getattr(parameter, 'enum', None)
        format_map = {
            'date-time': timezone.now().isoformat(),
            'date': timezone.now().date().isoformat(),
            'time': timezone.now().time().isoformat(),
            'password': '*' * min_length,
            'none': 'string'[:max_length] if min_length <= 6 else ('string' * (min_length // 6))[:min_length]
        }
        if enum:
            return enum[0]
        return format_map[getattr(parameter, 'format', 'none')]

    def process_number_parameter(self, parameter):
        minimum = getattr(parameter, 'minimum', 0)
        maximum = getattr(parameter, 'maximum', 100)
        enum = getattr(parameter, 'enum', None)
        if enum:
            return enum[0]
        elif minimum:
            return minimum
        elif maximum > 0:
            return 0
        else:
            return maximum

    def process_bool_parameter(self, parameter):
        return True

    def generate_example_value(self, parameter):
        param_type = getattr(parameter, 'type', 'string')
        type_map = {
            'string': self.process_string_parameter,
            'number': self.process_number_parameter,
            'integer': self.process_number_parameter,
            'boolean': self.process_bool_parameter
        }
        return type_map[param_type](parameter)

    def get_normalized_form_parameters(self):
        parameters = self.get_request_form_parameters(self.get_request_serializer())
        return OrderedDict([
            (parameter.name, self.generate_example_value(parameter)) for parameter in parameters if getattr(parameter, 'required', False)
        ])

    def get_normalized_query_parameters(self):
        parameters = self.get_query_parameters()
        return OrderedDict([
            (parameter.name, self.generate_example_value(parameter)) for parameter in parameters
        ])

    def get_x_code_samples(self):
        payload = self.get_normalized_form_parameters()
        query = self.get_normalized_query_parameters()
        headers = {
            'Authorization': f'Bearer {get_random_string(30)}',
            'Accept': self.get_produces()[0]
        }

        template_context = {
            "request_url": unquote_plus(self.request._request.build_absolute_uri(self.path)),
            "method": self.method,
            "payload": payload,
            "query": query,
            "headers": headers,
            "query_format": urlencode(query, safe='/@')
        }
        return [
            {
                'lang': 'curl',
                'source': render_to_string('project/docs/langs/curl.html', template_context)
            },
            {
                'lang': 'python',
                'source': render_to_string('project/docs/langs/python.html', template_context)
            },
            {
                'lang': 'javascript',
                'source': render_to_string('project/docs/langs/javascript.html', template_context)
            },
        ]

    def set_x_code_samples(self, operation):
        setattr(operation, 'x-code-samples', self.get_x_code_samples())
        return operation

    def get_operation(self, operation_keys):
        consumes = self.get_consumes()
        produces = self.get_produces()

        body = self.get_request_body_parameters(consumes)
        query = self.get_query_parameters()
        parameters = body + query
        parameters = [param for param in parameters if param is not None]
        parameters = self.add_manual_parameters(parameters)

        operation_id = self.get_operation_id(operation_keys)
        description = self.get_description()
        summary = self.get_summary()
        security = self.get_security()
        assert security is None or isinstance(security, list), "security must be a list of securiy requirement objects"
        deprecated = self.is_deprecated()
        tags = self.get_tags(operation_keys)

        responses = self.get_responses()

        operation = openapi.Operation(
            operation_id=operation_id,
            description=force_real_str(description),
            summary=force_real_str(summary),
            responses=responses,
            parameters=parameters,
            consumes=consumes,
            produces=produces,
            tags=tags,
            security=security,
            deprecated=deprecated
        )
        return self.set_x_code_samples(operation)


class CustomTagAutoSchema(XCodeSampleAutoSchema):
    """This schema generator looks for the view tag name in its definition
    If none is found, fallback to default behavior
    """

    def get_tags(self, operation_keys):
        if getattr(self.view, 'swagger_tags', None):
            return self.view.swagger_tags
        return super().get_tags(operation_keys)


class TaggedDescriptionSchemaGenerator(OpenAPISchemaGenerator):
    def get_schema(self, *args, **kwargs):
        swagger = super().get_schema(*args, **kwargs)
        tags = {tag for path in swagger.paths.items() for op in path[1].operations for tag in op[1].tags}
        swagger.tags = [tag_extra_data.get(tag, {'name': tag}) for tag in tags]
        return swagger
