"""
A simple example of retrieving the forecast for a single point and printing out in a human readable format
including converting the wind u and v fields to wind speed and direction.
"""
import argparse

from conversions import wind_direction_from_u_v, wind_speed_from_u_v
from utils import get_point_api_response, print_point_api_data


def print_point_api_response(lat, lon):
    """
    Fetch the forecast data and print it out for a given lat/lon.
    """

    # Build up a list of the values we want to print out from the response.
    data = []
    for entry in get_point_api_response(lat, lon):
        # Get the values we want to print out.
        issuance_time = entry['times']['issuance_time']
        valid_time = entry['times']['valid_time']
        air_temp = entry['values'].get('air_temperature')
        wind_u = entry['values'].get('eastward_wind')
        wind_v = entry['values'].get('northward_wind')

        # Convert the wind vectors to wind speed and direction.
        wind_direction = wind_direction_from_u_v(wind_u, wind_v)
        wind_speed = wind_speed_from_u_v(wind_u, wind_v)

        data.append([issuance_time, valid_time, air_temp, wind_speed, wind_direction])

    # Print out the values we have collected above in a friendly format.
    print_point_api_data(headers=['issuance_time', 'valid_time', 'air_temperature', 'wind_speed', 'wind_direction'], data=data)


if __name__ == '__main__':
    # Define our command line arguments
    parser = argparse.ArgumentParser(description='Print forecast data for a point')
    parser.add_argument('--lat', type=float, default=49.6,
                        help='The latitude of the point')
    parser.add_argument('--lon', type=float, default=6.1,
                        help='The longitude of the point')

    # Parse the command line arguments and invoke the function.
    args = parser.parse_args()
    print_point_api_response(args.lat, args.lon)
