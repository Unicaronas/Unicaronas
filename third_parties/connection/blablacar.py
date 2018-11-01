from django.conf import settings
from datetime import datetime
from .base import BaseConnection
from ..result import ResultItem


class BlaBlaCarConnection(BaseConnection):

    @property
    def connection_name(self):
        return 'blablacar'

    def get_parameters(self, query):
        url = "https://public-api.blablacar.com/api/v2/trips"
        headers = {
            'accept': 'application/json',
            'key': settings.BLABLACAR_API_KEY
        }
        params = {
            'fn': query.origin.query,
            'tn': query.destination.query,
            'locale': 'pt_BR',
            '_format': 'json',
            'cur': 'BRL',
            'db': query.datetime_gte.strftime('%Y-%m-%d %H:%M:%S'),
            'de': query.datetime_lte.strftime('%Y-%m-%d %H:%M:%S'),
            'aa': 0,
            'pmin': 0,
            'pmax': query.price_lte,
            'limit': 50
        }
        return {
            'url': url,
            'headers': headers,
            'params': params
        }

    def _normalize_response(self, response):
        trips = response['trips']
        results = []

        for trip in trips:
            url = trip['links']['_front']
            date_time = datetime.strptime(trip['departure_date'], "%d/%m/%Y %H:%M:%S")
            origin = trip['departure_place']['address']
            destination = trip['arrival_place']['address']
            price = trip['price']['value']
            result_item = ResultItem(
                url=url,
                date_time=date_time,
                origin=origin,
                destination=destination,
                price=price,
                source=self.connection_name
            )
            results.append(result_item)
        return results
