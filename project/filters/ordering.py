from rest_framework import filters as ofilters


class LocalizedOrderingFilter(ofilters.OrderingFilter):
    ordering_description = "Quais campos usar durante a ordenação dos resultados. Exemplo: `ordering=campo1,campo2`"
