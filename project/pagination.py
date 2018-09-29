from rest_framework.pagination import LimitOffsetPagination


class CustomLimitOffsetPagination(LimitOffsetPagination):
    default_limit = 10
    max_limit = 100
    limit_query_description = "Número de resultados retornados por página. Exemplo: `limit=20`"
    offset_query_description = "O índice inicial a partir do qual os resultados serão retornados. Exemplo: `offset=42`"
