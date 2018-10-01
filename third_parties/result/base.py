from datetime import datetime
from ..serializers import ResultItemSerializer, ResultSerializer


class BaseResultItem(object):
    """docstring for ResultItem"""

    serializer_class = ResultItemSerializer

    def __init__(self, origin, destination, price, date_time, url, source=None):
        assert isinstance(source, str)
        assert isinstance(origin, str)
        assert isinstance(destination, str)
        assert isinstance(price, int)
        assert isinstance(date_time, datetime)
        assert isinstance(url, str)
        self._source = source
        self._origin = origin
        self._destination = destination
        self._price = price
        self._datetime = date_time
        self._url = url

    @property
    def source(self):
        return self._source

    @property
    def origin(self):
        return self._origin

    @property
    def destination(self):
        return self._destination

    @property
    def price(self):
        return self._price

    @property
    def datetime(self):
        return self._datetime

    @property
    def url(self):
        return self._url

    @property
    def data(self):
        return {
            'origin': self.origin,
            'destination': self.destination,
            'price': self.price,
            'datetime': self.datetime,
            'url': self.url,
            'source': self.source
        }

    def get_serializer_class(self):
        return self.serializer_class

    def get_serializer_context(self):
        return {}

    def get_serializer(self, data, context={}):
        serializer_class = self.get_serializer_class()
        return serializer_class(data=data, context=context)

    @property
    def validated_data(self):
        data = self.data
        context = self.get_serializer_context()
        serializer = self.get_serializer(data=data, context=context)
        serializer.is_valid()
        return serializer.validated_data


class BaseResult(object):

    serializer_class = ResultSerializer

    def __init__(self, items=[]):
        self._items = items

    @property
    def items(self):
        return self._items

    @property
    def data(self):
        return {'results': [item.validated_data for item in self._items]}

    def get_serializer_class(self):
        return self.serializer_class

    def get_serializer_context(self):
        return {}

    def get_serializer(self, data, context={}):
        serializer_class = self.get_serializer_class()
        return serializer_class(data=data, context=context)

    @property
    def validated_data(self):
        data = self.data
        context = self.get_serializer_context()
        serializer = self.get_serializer(data=data, context=context)
        serializer.is_valid()
        return serializer.data

    def __add__(self, other):
        if not isinstance(self, BaseResult):
            raise TypeError(f"unsupported operand type(s) for +: '{type(self).__name__}' and '{type(other).__name__}'")
        data = self.items + other.items
        return self.__class__(data)

    def __radd__(self, other):
        return self.__add__(other)
