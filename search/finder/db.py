from django.utils import timezone
from .base import BaseFinder
from ..result import Result
from ..models import DBResult


class DBFinder(BaseFinder):

    def find_instance(self, term):
        qs = DBResult.objects.filter(expires__gt=timezone.now())
        return qs.filter(query__iexact=term.query).first()

    def find(self, term):
        # Only search for results that are not expired
        instance = self.find_instance(term)
        if instance is not None:
            return Result(instance.query, instance.address, instance.point, instance.address_components)
        return None

    def _search(self, term):
        premature_results = self.find(term)
        if premature_results is not None:
            return premature_results
        # Do magic with permutations
        return None

    def _cache(self, result):
        # Queries can be expired, so try to update
        # their addresses and point if they are
        DBResult.result_update_or_create(result)

    def _hit(self, term):
        instance = self.find_instance(term)
        if instance is not None:
            instance.hit(term)
