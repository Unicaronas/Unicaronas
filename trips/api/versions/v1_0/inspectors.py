from drf_yasg.inspectors import CoreAPICompatInspector
from drf_yasg.inspectors import NotHandled
from rest_framework_filters.backends import RestFrameworkFilterBackend
from rest_framework.settings import api_settings
from django.utils import timezone


def get_datetime():
    if api_settings.DATETIME_INPUT_FORMATS[0] == 'iso-8601':
        return timezone.now().isoformat()
    return timezone.now().strftime(api_settings.DATETIME_INPUT_FORMATS[0])


def get_date():
    if api_settings.DATE_INPUT_FORMATS[0] == 'iso-8601':
        return timezone.now().isoformat()
    return timezone.now().strftime(api_settings.DATE_INPUT_FORMATS[0])


def get_time():
    if api_settings.TIME_INPUT_FORMATS[0] == 'iso-8601':
        return timezone.now().isoformat()
    return timezone.now().strftime(api_settings.TIME_INPUT_FORMATS[0])


class DjangoFilterDescriptionInspector(CoreAPICompatInspector):
    def get_filter_parameters(self, filter_backend):
        print("Got filter_backends")
        print(filter_backend)
        if isinstance(filter_backend, RestFrameworkFilterBackend):
            result = super(DjangoFilterDescriptionInspector, self).get_filter_parameters(filter_backend)
            for param in result:
                if not param.get('description', ''):
                    field_data = param.name.split('__')
                    field_name = field_data[0]
                    if field_name == 'datetime':
                        param.type = 'string <date-time>'
                    if field_name == 'date':
                        param.type = 'string <date>'
                    if field_name == 'time':
                        param.type = 'string <time>'
                    field_query = field_data[1] if len(field_data) > 1 else 'exact'
                    field_query_map = {
                        'exact': 'iguais ao',
                        'gt': 'maiores que o',
                        'lt': 'menores que o',
                        'gte': 'maiores ou iguais ao',
                        'lte': 'menores ou iguais ao',
                    }
                    field_type_map = {
                        'string': 'texto',
                        'number': 5,
                        'string <date-time>': get_datetime,
                        'string <date>': get_date,
                        'string <time>': get_time,
                    }
                    if field_type_map.get(param.type, False):
                        if callable(field_type_map[param.type]):
                            v = field_type_map[param.type]()
                        else:
                            v = field_type_map[param.type]
                        doc_ex = f' Exemplo: `{param.name}={v}`'
                    else:
                        doc_ex = ''
                    param.description = f"Filtra a lista retornada por {field_name} retornando os valores {field_query_map[field_query]} termo.{doc_ex}"

            return result

        return NotHandled
