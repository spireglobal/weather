"""
A simple example of retrieving the forecast for a single point and printing out in a human readable format.
"""
import argparse

from utils import get_point_api_response, print_point_api_data


def print_point_api_response(lat, lon, bundles='basic'):
    """
    Fetch the forecast data and print it out for a given lat/lon.
    """

    # Build up a list of the values we want to print out from the response.
    data = []
    headers = []
    for entry in get_point_api_response(lat, lon, bundles=bundles, time_bundle='medium_range_high_freq'):
        # The dict is unsorted by default, this could cause issues as we iterate over each entry, so we make sure they are all sorted the same.
        sorted_values = sorted(entry['values'])

        issuance_time = entry['times']['issuance_time']
        valid_time = entry['times']['valid_time']

        # Get all the values that have been returned and merge them with the times.
        d = [issuance_time, valid_time] + [entry['values'][f] for f in sorted_values]
        data.append(d)

        headers.extend(['issuance_time', 'valid_time'] + sorted_values)

    # Print out the values we have collected above in a friendly format.
    print_point_api_data(headers=headers, data=data)


if __name__ == '__main__':
    # Define our command line arguments
    parser = argparse.ArgumentParser(description='Print forecasted temperatures for a point')
    parser.add_argument('--lat', type=float, default='49.6',
                        help='The latitude of the point')
    parser.add_argument('--lon', type=float, default='6.1',
                        help='The longitude of the point')
    parser.add_argument('--bundles', type=str, default='basic',
                        help='The bundles to include in csv format')

    # Parse the command line arguments and invoke the function.
    args = parser.parse_args()
    print_point_api_response(args.lat, args.lon, args.bundles)
