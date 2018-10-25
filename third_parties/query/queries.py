from .base import BaseSearchQuery


class SearchQuery(BaseSearchQuery):

    def __str__(self):
        return f"Query: (dest '{self.destination.query[:10]}', ori '{self.origin.query[:10]}', dt_gt '{self.datetime_gte}', dt_lt '{self.datetime_lte}', price '{self.price_lte}')"
