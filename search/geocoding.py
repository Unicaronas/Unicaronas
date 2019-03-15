import requests
from django.conf import settings
from django.contrib.gis.geos.collections import Point


def extract_data_from_response(data, idx=0):
    """
    Given some data, extract the formatted address and the geometry point
    """
    if data['status'] != 'OK':
        raise ValueError('Given data contains no information')
    results = data['results'][idx]
    formatted_address = results['formatted_address']
    latitude = results['geometry']['location']['lat']
    longitude = results['geometry']['location']['lng']
    return formatted_address, Point(latitude, longitude), results['address_components']


def geocode_address(address):
    """
    Given a typed address, use google's api to fetch
    the formatted address and the geometry point
    """
    url = "https://maps.googleapis.com/maps/api/geocode/json"
    api_key = settings.GEOCODING_API_KEY
    payload = {
        'address': address,
        'key': api_key,
        'region': 'br',
        'language': 'pt-BR'
    }
    r = requests.get(url, params=payload)
    r.raise_for_status()
    data = r.json()
    return extract_data_from_response(data)


def reverse_geocode(point):
    """
    Given a geometry point, use google's api to fetch
    the formatted address and the geometry point
    """
    url = "https://maps.googleapis.com/maps/api/geocode/json"
    api_key = settings.GEOCODING_API_KEY
    payload = {
        'latlng': f"{point.coords[0]},{point.coords[1]}",
        'key': api_key,
        'region': 'br'
    }
    r = requests.get(url, params=payload)
    r.raise_for_status()
    data = r.json()
    return extract_data_from_response(data)


def map_common_results(address):
    """
    Take an address and try to map it to
    common, correct, addresses
    """
    # Implement this
    return address
