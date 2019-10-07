import argparse

import pygrib


def print_variables_for_single_coordinate(filepath, lat, lon):
    """
    Print all of the variables in the grib file
    """
    grib = pygrib.open(filepath)

    # Print an inventory of all messages in the grib file.
    for msg in grib:
        print(msg.name, msg.data(lat1=lat, lat2=lat, lon1=lon, lon2=lon)[0][0][0])


def print_select_variables_for_single_coordinate(filepath, lat, lon):
    """
    Print just temperature and precipitation variables from the grib file
    """
    grib = pygrib.open(filepath)

    # Select only the temperature precipitation messages.
    temperature_message = grib.select(name='2 metre temperature')[0]
    precipitation_message = grib.select(name='Total Precipitation')[0]

    point_temperature = temperature_message.data(lat1=lat, lat2=lat, lon1=lon, lon2=lon)[0][0][0]
    point_precipitation = precipitation_message.data(lat1=lat, lat2=lat, lon1=lon, lon2=lon)[0][0][0]

    print('Temperature: %s' % point_temperature)
    print('Total Precipitation: %s' % point_precipitation)


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Open a grib2 file using pygrib')
    parser.add_argument('filepath', type=str,
                        help='The path to the file to open')
    parser.add_argument('--lat', type=float, default='49.6',
                        help='The latitude of the point')
    parser.add_argument('--lon', type=float, default='6.1',
                        help='The longitude of the point')

    args = parser.parse_args()
    print_variables_for_single_coordinate(args.filepath, args.lat, args.lon)
    print_select_variables_for_single_coordinate(args.filepath, args.lat, args.lon)
