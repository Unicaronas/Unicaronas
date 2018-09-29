from rest_framework.generics import ListAPIView, RetrieveAPIView
from ..mixins import PrefetchQuerysetModelMixin


class PrefetchListAPIView(
        PrefetchQuerysetModelMixin,
        ListAPIView):
    """
    Concrete view for listing a prefetched queryset.
    """
    pass


class PrefetchRetrieveAPIView(
        PrefetchQuerysetModelMixin,
        RetrieveAPIView):
    """
    Concrete view for retrieving a prefetched queryset.
    """
    pass
