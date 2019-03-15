from django.contrib.gis.geos.collections import Point


class BaseResult(object):
    """Base Result
    Represents a search result
    """

    def __init__(self, query, address, point, address_components):
        assert isinstance(query, str)
        assert isinstance(address, str)
        assert isinstance(point, Point)
        assert isinstance(address_components, list)
        self._query = query
        self._address = address
        self._point = point
        self._address_components = address_components

    @property
    def query(self):
        return self._query

    @property
    def address(self):
        return self._address

    @property
    def point(self):
        return self._point

    @property
    def latitude(self):
        return self.point.coords[0]

    @property
    def longitude(self):
        return self.point.coords[1]

    @property
    def coords(self):
        return self.latitude, self.longitude

    @property
    def address_components(self):
        return self._address_components

    @property
    def dict_coords(self):
        return {'latitude': self.latitude, 'longitude': self.longitude}

    def __str__(self):
        return f"Result of: {self.query}"

    def __repr__(self):
        return str(self)
