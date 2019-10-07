import argparse

import Nio


def print_variables_for_single_coordinate(filepath, lat, lon):
    file = Nio.open_file(filepath, mode='r', format='grib')

    # Retrieve the temperature field from the file variables.
    temperature_field = file.variables['TMP_P0_L103_GLL0']

    # Using NIO Extended Selection, select the value for the given lat/lon.
    print(temperature_field['lat_0|%s lon_0|%s' % (lat, lon)])


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Open a grib2 file using pynio')
    parser.add_argument('filepath', type=str,
                        help='The path to the file to open')
    parser.add_argument('--lat', type=float, default='49.6',
                        help='The latitude of the point')
    parser.add_argument('--lon', type=float, default='6.1',
                        help='The longitude of the point')

    args = parser.parse_args()
    print_variables_for_single_coordinate(args.filepath, args.lat, args.lon)
