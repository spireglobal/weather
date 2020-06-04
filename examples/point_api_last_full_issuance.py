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
# local scripts
import utils

HOST = 'https://api.wx.spire.com'
API_KEY = os.getenv('spire-api-key')


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


def get_last_complete_issuance(api_key, lat, lon, bundles, time_bundle, issuance_time=None):
    # Construct an API request 
    data = utils.get_point_api_response(
        lat, lon, bundles=bundles, time_bundle=time_bundle, issuance_time=issuance_time, api_key=api_key
    )
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
        # Try a new API request with the previous issuance time
        get_last_complete_issuance(api_key, lat, lon, bundles, time_bundle, it_string)
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
    parser.add_argument('--bundles', type=str,
                        help='The weather bundles for the forecast', default='basic')
    parser.add_argument('--time_bundle', type=str,
                        help='The time bundle for the forecast', default='medium_range_high_freq')

    args = parser.parse_args()
    # Make an API request without specifying an issuance time
    get_last_complete_issuance(API_KEY, args.lat, args.lon, args.bundles, args.time_bundle)