"""
The Spire Weather Point API gives forecast-total accumulated precipitation values since the start of
the forecast rather than fixed interval accumulations such as 6 hour or 24 hour values. This example
shows how a user could create 6-hour accumulations from the forecast-total value by differencing
the totals from adjacant lead times.
"""
import argparse
import os
from urllib.parse import urljoin

import requests
from tabulate import tabulate

HOST = 'https://api.wx.spire.com'
API_KEY = os.getenv('spire-api-key')


def print_point_api_response(api_key, lat, lon):
    """
    Fetch the forecast data and print it out for a given lat/lon.
    """

    print(f'Retrieving forecast for point ({lat},{lon})')

    # Build the URL, add the headers and query parameters.
    url = urljoin(HOST, '/forecast/point')
    params = {'lat': lat, 'lon': lon}
    headers = {'spire-api-key': api_key}
    response = requests.get(url, headers=headers, params=params)

    # If there is no 'data' element then raise an error.
    json_response = response.json()
    if 'data' not in json_response:
        raise Exception('Response did not contain a data element', json_response)

    data = json_response['data']

    # Build up a list of the values we want to print out from the response.
    tabular_data = []
    previous_precip_total = 0
    for entry in data:
        valid_time = entry['times']['valid_time']

        # Create the accumulation during the period between the previous output time and the current one.
        current_precip_total = entry['values']['precipitation_amount']
        precip_amount = current_precip_total - previous_precip_total
        previous_precip_total = current_precip_total

        tabular_data.append([valid_time, precip_amount])

    # Using the tabulate library, print out the values we have collected above in a friendly format.
    print(tabulate(tabular_data, headers=['valid_time', 'precipitation_amount']))


if __name__ == '__main__':
    if not API_KEY:
        raise Exception('spire-api-key environment variable is not set.')

    # Define our command line arguments
    parser = argparse.ArgumentParser(description='Print forecast precipitation for a point')
    parser.add_argument('--lat', type=float, default=49.6,
                        help='The latitude of the point')
    parser.add_argument('--lon', type=float, default=6.1,
                        help='The longitude of the point')

    # Parse the command line arguments and invoke the function.
    args = parser.parse_args()
    print_point_api_response(API_KEY, args.lat, args.lon)
