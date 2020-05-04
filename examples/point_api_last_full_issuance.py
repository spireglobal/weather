"""
Example of how to use the Spire Weather Point API to download forecast data for a particular product
bundle and time bundle. This code is set up to download the latest full forecast issuance,
thereby ignoring the most recent forecast if it is incomplete and still populating the API.
"""
import argparse
import os
from urllib.parse import urljoin
from datetime import timedelta
import dateutil.parser
import requests

HOST = 'https://api.wx.spire.com'
API_KEY = os.getenv('spire-api-key')


def make_request(api_key, lat, lon, time_bundle, issuance_time):
    # Build the URL, add the headers and query parameters.
    url = urljoin(HOST, '/forecast/point')
    params = {
        'bundles': 'basic',
        'time_bundle': time_bundle,
        'lat': lat,
        'lon': lon
    }
    # Add the `issuance_time` parameter if it is specified
    if issuance_time != None:
        params['issuance_time'] = issuance_time
    # Set the auth header
    headers = {'spire-api-key': api_key}
    # Make the API request
    response = requests.get(url, headers=headers, params=params)
    # Return the API response
    return response


def get_response_data(response):
    # Convert the raw response into JSON format
    json_response = response.json()
    # Ensure the 'data' field is present
    if 'data' not in json_response:
        raise Exception('Response did not contain a data element', json_response)
    # Return the response data
    return json_response['data']


def get_expected_forecast_size(time_bundle):
    if time_bundle == 'short_range_high_freq':
        # The short range, high time frequency bundle contains data for 25 lead times (or steps)
        # representing forecasts at 1 hour intervals from 0 to 24 hours.
        return 25
    elif time_bundle == 'medium_range_std_freq':
        # The medium range, standard time frequency bundle contains data for 29 lead times (or steps)
        # representing forecasts at six hour intervals from 0 to 168 hours.
        return 29
    elif time_bundle == 'medium_range_high_freq':
        # The medium range, high time frequency bundle contains data for 49 lead times (or steps)
        # representing forecasts at 1 hour intervals from 0 to 24 hours,
        # as well as 6 hour intervals up to 168 hours.
        return 49
    else:
        raise Exception('Unexpected time bundle', time_bundle)


def get_last_complete_issuance(api_key, lat, lon, time_bundle, issuance_time=None):
    # Construct an API request 
    response = make_request(api_key, lat, lon, time_bundle, issuance_time)
    # Get the response data
    data = get_response_data(response)
    # Get the expected forecast size for the specified time bundle
    expected_data_size = get_expected_forecast_size(time_bundle)
    # Check if the returned forecast is a complete issuance for this time bundle
    if len(data) != expected_data_size:
        # Retrieve the 'issuance_time' from the first item in the data array
        issuance_time = data[0]['times']['issuance_time']
        # Convert the 'issuance_time' string into a Python datetime object
        dt = dateutil.parser.isoparse(issuance_time)
        # Determine the time delta between the current and previous issuance
        if 'medium_range' in time_bundle:
            # Medium range forecasts are issued every 12 hours
            delta = 12
        else:
            # Short range forecasts are issed every 6 hours
            delta = 6
        # Get the previous issuance time
        prev_issuance_time = dt - timedelta(hours=delta)
        # Convert the issuance time into a string
        it_string = prev_issuance_time.isoformat()
        # Construct a new API request
        response = make_request(api_key, lat, lon, time_bundle, it_string)
        # Get the response data
        data = get_response_data(response)
    # Print the response data
    print('Response data:', data)


if __name__ == '__main__':
    if not API_KEY:
        raise Exception('spire-api-key environment variable is not set.')

    parser = argparse.ArgumentParser(description='Download last full forecast issuance for a location')
    parser.add_argument('--lat', type=float, default=49.6,
                        help='The latitude of the point')
    parser.add_argument('--lon', type=float, default=6.1,
                        help='The longitude of the point')
    parser.add_argument('--time_bundle', type=str,
                        help='The time bundle for the forecast', default='medium_range_high_freq')

    args = parser.parse_args()
    get_last_complete_issuance(API_KEY, args.lat, args.lon, args.time_bundle)