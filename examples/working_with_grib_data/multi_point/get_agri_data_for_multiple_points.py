"""
Read list of coordinate pairs from a CSV file input,
extract point values from multiple Agricultural GRIB files,
and export result into a new CSV.

This program will extract data from a collection of GRIB files at various
geographic locations. Since each GRIB file represents a valid forecast time,
this program can be used to aggregate point data over the course of a new
forecast or a series of previous forecasts (e.g. 1 month of historical data)

Bilinear interpolation is performed on the data to obtain the point values if
the chosen location is not one of the grid points from the forecast fields.
"""
from __future__ import print_function
from datetime import datetime, timedelta
import argparse
import glob
import csv
import sys
import os

import Nio


# The default set of fields to extract if none are provided on the command line.
# The simplest way to get this list is to open the file and print the file object:
#
# nc = Nio.open_file(...)
# print(nc)
# nc.close()
#
# Here we default to all of the fields in the agricultural bundle
DEF_VARIABLES = (
    'TMP_P0_L1_GLL0',        # Temperature
    'LHTFL_P0_L1_GLL0',      # Latent heat net flux
    'SHTFL_P0_L1_GLL0',      # Sensible heat net flux
    'SPFH_P0_L103_GLL0',     # Specific humidity
    'TSOIL_P0_2L106_GLL0',   # Soil temperature at multiple depths below land surface
    'SOILW_P0_2L106_GLL0',   # Volumetric soil moisture content at multiple depths below land surface
    'DSWRF_P8_L1_GLL0_acc',  # Downward short-wave radiation flux
    'USWRF_P8_L1_GLL0_acc',  # Upward short-wave radiation flux
    'DLWRF_P8_L1_GLL0_acc',  # Downward long-wave rad. flux
    'ULWRF_P8_L1_GLL0_acc',  # Upward long-wave rad. flux
    'ULWRF_P8_L8_GLL0_acc',  # Upward long-wave rad. flux (nominal top of atmosphere)
)

# Build a dictionary row object for the output CSV
def create_row(time, lat, lon, depth, name, value, units):
    return {
        'Datetime': time,
        'Latitude': lat,
        'Longitude': lon,
        'Depth': depth,
        'Variable': name,
        'Value': value,
        'Units': units
    }

# Parse the datetime out of a grib2 filename,
# assuming it is in the following format:
# sof-d.20200317.t06z.0p125.agricultural.global.f000.grib2
def parse_datetime(filename):
    parts = filename.split('.')
    date = parts[1]
    year = int(date[0:4])
    month = int(date[4:6])
    day = int(date[6:8])
    # Strip `t` and `z` and parse the issuance time integer
    issuance_time = parts[2]
    issuance_time = int(issuance_time[1:3])
    # Strip `f` and parse the lead time integer
    lead_time = parts[-2]
    lead_time = int(lead_time[1:])
    # Combine issuance and lead times to get valid hours
    hours = issuance_time + lead_time
    return datetime(year, month, day) + timedelta(hours=hours)

# Extract data from a grib2 file at multiple point locations
# and return an array of dictionary row objects
def process_file(filename, variables, points):
    print('Processing', filename)
    nc = Nio.open_file(filename, mode='r', format='grib')
    # Parse the datetime out of the filename
    time = parse_datetime(filename)
    # Iterate through list of point locations
    # and extract data for each into a python dict
    rows = []
    for point in points:
        lat = point[0]
        lon = point[1]
        # Use PyNio's extended selection to do the interpolation for us.
        # https://www.pyngl.ucar.edu/NioExtendedSelection.shtml
        # Here we specify latitude, longitude, and all depths below land surface
        select = 'lat_0|{lat}i lon_0|{lon}i lv_DBLL0|:'.format(lat=lat, lon=lon)
        # Iterate through variables to collect the data
        for name in variables:
            if name in nc.variables:
                var = nc.variables[name]
                value = var[select]
                units = var.attributes['units']
                # Soil Moisture and Soil Temperature values are arrays
                # containing data at 4 different depths, so 4 distinct rows are added for each
                if 'SOIL' in name:
                    rows.append(create_row(time, lat, lon, '0-10cm', name, value[0], units))
                    rows.append(create_row(time, lat, lon, '10-40cm', name, value[1], units))
                    rows.append(create_row(time, lat, lon, '40-100cm', name, value[2], units))
                    rows.append(create_row(time, lat, lon, '100-200cm', name, value[3], units))
                    # Continue iterating through the variable names
                    continue
            else:
                # Variable name was not found
                # so indicate in the output that data is missing
                value = units = 'Missing'
            # Append a single row of data for this variable
            # with a null depth value since it is not related to `SOIL`
            rows.append(create_row(time, lat, lon, None, name, value, units))
    nc.close()
    return rows

# Extract point data from a collection of grib2 files
# and write it to a CSV output file
def process_files(data_dir, points, variables):
    # Read all grib2 files in the specified directory
    filepath = os.path.join(data_dir, '*.grib2')
    filenames = glob.glob(filepath)
    # Sort the filenames alphabetically
    filenames = sorted(filenames)
    # For each grib2 file, extract data from all point locatons
    # that are specified in the input CSV
    data = []
    for filename in filenames:
        rows = process_file(filename, variables, points)
        data.append(rows)
    # Set the fieldnames for the output CSV
    headers = ['Datetime', 'Latitude', 'Longitude', 'Depth', 'Variable', 'Value', 'Units']
    # Write the extracted data to the output CSV
    with open('output.csv', 'w') as outfile:
        writer = csv.DictWriter(outfile, fieldnames=headers)
        writer.writeheader()
        for rows in data:
            writer.writerows(rows)

if __name__ == '__main__':
    parser = argparse.ArgumentParser(
        description='Extract data for a list of points from multiple forecast files'
    )
    parser.add_argument('-v', '--variables', type=str,
                        help='The fields to extract at each point (separated by commas)')
    parser.add_argument('points_csv', type=str,
                        help='The input CSV file with `latitude` and `longitude` columns. See `example_points.csv`')
    parser.add_argument('data_dir', type=str,
                        help='The directory containing properly formatted .grib2 files to extract from')

    args = parser.parse_args()
    # Parse the list of provided variable names or use the default defined above
    variables = args.variables.split(',') if args.variables else DEF_VARIABLES
    # Read the point locations from the input CSV
    locations = []
    with open(args.points_csv, 'r') as csvfile:
        reader = csv.DictReader(csvfile)
        for row in reader:
            lat = row['latitude']
            lon = row['longitude']
            locations.append( [lat, lon] )
    # Process all files in the specified data directory
    process_files(args.data_dir, locations, variables)
