from drf_yasg.inspectors.view import SwaggerAutoSchema
from drf_yasg.generators import OpenAPISchemaGenerator


tag_extra_data = {
    'Motorista': {
        'name': 'Motorista',
        'description': """
Nossa API de motoristas lhe permite construir serviços e soluções que tornam as vidas dos motoristas mais fáceis. Com a permissão do motorista, você consegue gerenciar caronas, passageiros e mais.

## Caronas
Ajude motoristas a gerenciar suas caronas, criando, listando e editando todas as viagens que decidirem fazer.

## Passageiros
Dê total controle aos seus motoristas sobre quem vai ou não em suas caronas. Gerencie aprovação e rejeição de passageiros e use os dados fornecidos para ajudar seus motoristas a fazerem viagens seguras e tranquilas.
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
    }
}


class CustomTagAutoSchema(SwaggerAutoSchema):
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
