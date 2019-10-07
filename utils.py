import os
from urllib.parse import urljoin

import requests
from tabulate import tabulate

HOST = 'https://api.wx.spire.com'


def get_api_key():
    api_key = os.getenv('spire-api-key')
    if not api_key:
        raise Exception('API_KEY environment variable is not set.')

    return api_key


def get_point_api_response(lat, lon, bundles=None, time_bundle=None, valid_time_interval=None, api_key=get_api_key()):
    """
    Fetch the point forecast data.
    """

    print(f'Retrieving forecast for point ({lat},{lon})')

    # Build the URL, add the headers and query parameters.
    url = urljoin(HOST, '/forecast/point')
    params = {'lat': lat, 'lon': lon}

    if bundles:
        params['bundles'] = bundles
    if time_bundle:
        params['time_bundle'] = time_bundle
    if valid_time_interval:
        params['valid_time_interval'] = valid_time_interval

    headers = {'spire-api-key': api_key}
    response = requests.get(url, headers=headers, params=params)

    # If there is no 'data' element then raise an error.
    json_response = response.json()
    if 'data' not in json_response:
        raise Exception('Response did not contain a data element', json_response)

    return json_response['data']


def print_point_api_data(headers, data):
    print(tabulate(data, headers=headers))
