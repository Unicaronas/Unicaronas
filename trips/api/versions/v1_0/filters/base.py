from django.db.models import F, Q, Sum
from django.db.models.functions import Coalesce
from django.contrib.gis.measure import D
from rest_framework_filters import FilterSet, filters
from rest_framework import filters as ofilters
from search.pipeline import RequestPipeline
from .....models import Trip


class TripFilterSet(FilterSet):
    seats_left__gte = filters.NumberFilter(
        label="Assentos restantes ou mais", method='get_seats_left')
    origin_radius = filters.NumberFilter(
        label="Raio de pesquisa na origem em km", method='get_radius')
    destination_radius = filters.NumberFilter(
        label="Raio de pesquisa no destino em km", method='get_radius')
    origin = filters.CharFilter(
        label="Endereço de origem", method='get_origin')
    destination = filters.CharFilter(
        label="Endereço de destino", method='get_destination')

    def get_seats_left(self, qs, name, value):
        seats_left = F('max_seats') - Coalesce(Sum('passengers__seats',
                                                   filter=~Q(passengers__status="denied")), 0)
        qs = qs.annotate(s_left=seats_left)
        val = value
        expr = name.split('__')[1] if len(name.split('__')) > 1 else 'exact'
        return qs.filter(**{f's_left__{expr}': val})

    def get_radius(self, qs, name, value):
        return qs

    def get_origin(self, qs, name, value):
        radius = self.data.get('origin_radius', '5')
        if not radius:
            radius = '5'
        radius = min(max(float(radius), 0.05), 10)
        pipe = RequestPipeline('origin', self.request)
        result = pipe.search(value)
        if result is None:
            return qs.none()
        return qs.filter(origin_point__distance_lte=(result.point, D(km=radius)))

    def get_destination(self, qs, name, value):
        radius = self.data.get('destination_radius', '5')
        if not radius:
            radius = '5'
        radius = min(max(float(radius), 0.05), 20)
        pipe = RequestPipeline('destination', self.request)
        result = pipe.search(value)
        if result is None:
            return qs.none()
        return qs.filter(destination_point__distance_lte=(result.point, D(km=radius)))

    class Meta:
        model = Trip
        fields = {
            'price': ['lte'],
            'datetime': ['exact', 'gte', 'lte'],
            'auto_approve': ['exact']
        }


class LocalizedOrderingFilter(ofilters.OrderingFilter):
    ordering_description = "Quais campos usar durante a ordenação dos resultados. Exemplo: `ordering=campo1,campo2`"
