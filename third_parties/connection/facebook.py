from dateutil.parser import parse
from search.term import Term
from search.finder import GrammarCorrectorFinder, TermPreparationFinder
from .base import BaseConnection
from ..models import FacebookGroup
from ..fb_search_tools import process_item


class FacebookConnection(BaseConnection):

    def __init__(self, fb_group_id):
        self.fb_group = FacebookGroup.objects.filter(id=fb_group_id).first()
        super().__init__()

    @property
    def connection_name(self):
        # 'fb-' + self.fb_group.name
        return 'facebook'

    @property
    def is_expired(self):
        return self.fb_group is None or self.fb_group.is_expired

    def get_group_id(self):
        return self.fb_group.group_id

    def get_access_token(self):
        return self.fb_group.token

    def get_parameters(self, query):
        group_id = self.get_group_id()
        access_token = self.get_access_token()
        url = f'https://graph.facebook.com/v3.1/{group_id}/feed/'
        params = {
            'access_token': access_token,
            'fields': 'message,created_time,id',
            'limit': 100
        }
        return {'url': url, 'params': params}

    def get_source(self):
        return self.connection_name

    def pre_process_item(self, raw_data):
        message = raw_data.get('message', None)
        if message is None:
            return None
        term = Term(message)
        term = TermPreparationFinder().transform(term)
        term = GrammarCorrectorFinder().transform(term)
        raw_data['message'] = term.query
        raw_data['created_time'] = parse(raw_data['created_time'])
        return raw_data

    def _normalize_response(self, response):
        raw_data = response['data']
        source = self.get_source()
        data = []
        for raw_item in raw_data:
            item = self.pre_process_item(raw_item)
            if item is None:
                continue
            result_item = process_item(item, source)
            if result_item is None:
                continue
            data.append(result_item)
        return data

    def filter_price(self, response, query):
        price_lte = query.price_lte
        return filter(lambda item: item.price <= price_lte, response)

    def filter_datetime(self, response, query):
        datetime_lte = query.datetime_lte
        datetime_gte = query.datetime_gte
        return filter(lambda item: datetime_gte <= item.datetime <= datetime_lte, response)

    def filter_origin(self, response, query):
        origin = query.origin.query
        return filter(lambda item: origin == item.origin, response)

    def filter_destination(self, response, query):
        destination = query.destination.query
        return filter(lambda item: destination == item.destination, response)

    def filter_response(self, response, query):
        """Perform additional filtering"""
        response = self.filter_datetime(response, query)
        response = self.filter_destination(response, query)
        response = self.filter_origin(response, query)
        response = self.filter_price(response, query)
        return list(response)
