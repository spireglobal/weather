"""
Demonstrate how to extract data from several GRIB messages using PyGRIB 

https://github.com/jswhit/pygrib/
"""
import argparse

import pygrib


def print_variables_for_single_coordinate(filepath, lat, lon):
    """
    Print all of the variables in the GRIB file
    """
    grib = pygrib.open(filepath)

    for msg in grib:
        print(msg.name, msg.data(lat1=lat, lat2=lat, lon1=lon, lon2=lon)[0][0][0])


def print_select_variables_for_single_coordinate(filepath, lat, lon):
    """
    Extract and print just temperature and precipitation variables from the GRIB file
    """
    grib = pygrib.open(filepath)

    # Select only the 2-m temperature and precipitation messages.
    temperature_message = grib.select(name='2 metre temperature')[0]
    precipitation_message = grib.select(name='Total Precipitation')[0]

    point_temperature = temperature_message.data(lat1=lat, lat2=lat, lon1=lon, lon2=lon)[0][0][0]
    point_precipitation = precipitation_message.data(lat1=lat, lat2=lat, lon1=lon, lon2=lon)[0][0][0]

    print('Temperature: %s' % point_temperature)
    print('Total Precipitation: %s' % point_precipitation)


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Extract and print data from a GRIB file using pygrib')
    parser.add_argument('filepath', type=str,
                        help='The path to the file to open')
    parser.add_argument('--lat', type=float, default=49.6,
                        help='The latitude of the point')
    parser.add_argument('--lon', type=float, default=6.1,
                        help='The longitude of the point')

    args = parser.parse_args()
    print_variables_for_single_coordinate(args.filepath, args.lat, args.lon)
    print_select_variables_for_single_coordinate(args.filepath, args.lat, args.lon)
