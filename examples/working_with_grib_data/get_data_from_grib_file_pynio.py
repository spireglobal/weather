"""
Extract point values from GRIB messages

This program will extract data from a collection of GRIB messages at a single
geographic location.

Bilinear interpolation is performed on the data to obtain the point values if
the chosen location is not one of the grid points from the forecast fields.
"""
from __future__ import print_function
import argparse
import csv
import sys

import Nio


# The default set of fields to extract if none are provided on the command line.
# The simplest way to get this list is to open the file and print the file object:
#
# nc = Nio.open_file(...)
# print(nc)
# nc.close()
#
# Here we default to all of the fields in the basic bundle
DEF_VARIABLES = (
    'TMP_P0_L103_GLL0',     # 2-m temperature
    'DPT_P0_L103_GLL0',     # 2-m dewpoint temperature
    'RH_P0_L103_GLL0',      # 2-m relative humidity
    'UGRD_P0_L103_GLL0',    # eastward-component of the wind at 10 meters
    'VGRD_P0_L103_GLL0',    # northward-component of the wind at 10 meters
    'GUST_P0_L1_GLL0',      # wind gust speed at 10 meters
    'PRMSL_P0_L101_GLL0',   # mean sea-level pressure
    'APCP_P8_L1_GLL0_acc',  # accumulated precipitation amount
)

def process_file(filename, variables, lat, lon):
    # Use PyNio's extended selection to do the interpolation for us.
    # https://www.pyngl.ucar.edu/NioExtendedSelection.shtml
    # Here all variables are 2-D. If 3-D (or higher dimension) fields will be extracted
    # the pattern will need to be adjusted.
    select = 'lat_0|{lat}i lon_0|{lon}i'.format(lat=lat, lon=lon)

    data = []
    nc = Nio.open_file(filename, mode='r', format='grib')
    for name in variables:
        if name in nc.variables:
            var = nc.variables[name]
            value = var[select]
            units = var.attributes['units']
        else:
            value = units = 'Missing'
        data.append([name, value, units])
    nc.close()

    writer = csv.writer(sys.stdout)
    writer.writerow(('Variable', 'Value', 'Units'))
    writer.writerows(data)


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Extract point data from forecast files')
    parser.add_argument('-v', '--variables', type=str,
                        help='The fields to extract at the point (separate by commas')
    parser.add_argument('filename', type=str,
                        help='The file to extract point data from')
    parser.add_argument('latitude', type=float,
                        help='The latitude of the extraction point')
    parser.add_argument('longitude', type=float,
                        help='The longitude (0-360) of the extraction point')

    args = parser.parse_args()
    variables = args.variables.split(',') if args.variables else DEF_VARIABLES
    process_file(args.filename, variables, args.latitude, args.longitude)
