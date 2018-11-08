from django.contrib.gis.geos import Point
from django.contrib.gis.geos.error import GEOSException
from rest_framework import serializers
from ..mixins import QueryFieldsMixin


class PointSerializer(
        QueryFieldsMixin,
        serializers.Serializer):

    latitude = serializers.FloatField()
    longitude = serializers.FloatField()

    def run_validation(self, data=serializers.empty):
        """
        We override the default `run_validation`, because the validation
        performed by validators and the `.validate()` method should
        be coerced into an error dictionary with a 'non_fields_error' key.
        """
        (is_empty_value, data) = self.validate_empty_values(data)
        if is_empty_value:
            return data

        value = self.to_internal_value(data)
        try:
            self.run_validators(value)
            value = self.validate(value)
            assert value is not None, '.validate() should return the validated data'
        except (serializers.ValidationError) as exc:
            raise serializers.ValidationError(detail=exc)

        return value

    def run_validators(self, value):
        value = self.to_representation(value)
        super().run_validators(value)

    def to_representation(self, value):
        if isinstance(value, dict) or value is None:
            return value
        coords = value.coords
        geojson = {'latitude': coords[0], 'longitude': coords[1]}
        return geojson

    def to_internal_value(self, value):
        if value == '' or value is None:
            return value
        if isinstance(value, Point):
            # value already has the correct representation
            return value
        if isinstance(value, dict):
            value = tuple(map(lambda v: float(v), value.values()))
        try:
            return Point(value)
        except (GEOSException):
            raise serializers.ValidationError(
                'Formato inválido: Não foi possível converter a string pra um Point')
        except (ValueError, TypeError) as e:
            raise serializers.ValidationError(
                'Unable to convert to python object: {}'.format(str(e)))
