from django import forms
from django.db.models import Count, F, Q
from rest_framework_filters import FilterSet, filters
from rest_framework import filters as ofilters
from .....models import Trip


class TripFilterSet(FilterSet):
    seats_left = filters.LookupChoiceFilter(
        label="Assentos vagos",
        method="get_seats_left",
        lookup_choices=['exact', 'gt', 'gte', 'lt', 'lte'],
        field_class=forms.IntegerField
    )

    def get_seats_left(self, qs, name, value):
        seats_left = F('max_seats') - Count('passengers',
                                            filter=~Q(passengers__status="denied"))
        qs = qs.annotate(s_left=seats_left)
        val = value[0]
        expr = value[1]
        return qs.filter(**{f's_left__{expr}': val})

    class Meta:
        model = Trip
        fields = {
            'price': ['exact', 'gt', 'gte', 'lt', 'lte'],
            'datetime': ['exact', 'gt', 'gte', 'lt', 'lte'],
            'auto_approve': ['exact'],
            'seats_left': ['exact', 'gt', 'gte', 'lt', 'lte']
        }


class LocalizedOrderingFilter(ofilters.OrderingFilter):
    ordering_description = "Quais campos usar durante a ordenação dos resultados. Exemplo: `ordering=campo1,campo2`"
