"""
Extract regional values from an Upper-Air GRIB file at one vertical level

This program extracts temperature data from a GRIB file
at a single vertical (isobaric) level. It then crops the data
to the horizontal area of a provided shapefile.
"""
import argparse
import xarray as xr
import pandas as pd
import matplotlib.pyplot as plt
from osgeo.ogr import GetDriverByName
import os
import sys
dir_path = os.path.dirname(os.path.realpath(__file__))
parent = os.path.join(dir_path, os.pardir)
sys.path.append(os.path.join(parent,'..'))
from conversions import wind_speed_from_u_v, wind_direction_from_u_v
from utils_grib import coarse_geo_filter, precise_geo_filter
# Load the shapefile area
filename = os.path.join(dir_path, 'shpfile/italy.shp')
driver = GetDriverByName('ESRI Shapefile')
shpfile = driver.Open(filename)
AREA = shpfile.GetLayer()

# DEF_VARIABLES = (
#     'TMP_P0_L100_GLL0',    # Temperature
#     'RH_P0_L100_GLL0',     # Relative humidity
#     'CLWMR_P0_L100_GLL0',  # Cloud mixing ratio
#     'ICMR_P0_L100_GLL0',   # Ice water mixing ratio
#     'UGRD_P0_L100_GLL0',   # U-component of wind
#     'VGRD_P0_L100_GLL0',   # V-component of wind
#     'DZDT_P0_L100_GLL0',   # Vertical velocity (geometric)
#     'ABSV_P0_L100_GLL0',   # Absolute vorticity
#     'HGT_P0_L100_GLL0',    # Geopotential height
#     'lv_ISBL1',            # Isobaric surface
#     'lat_0',               # latitude
#     'lon_0',               # longitude
#     'lv_ISBL0',            # Isobaric surface
# )

# Create a dictionary for isobaric levels in hPa
# and corresponding values in pascals
isobaric_levels = {
    '1000hPa': 100000, '950hPa': 95000, '925hPa': 92500, '900hPa': 90000,
    '850hPa':  85000,  '800hPa': 80000, '700hPa': 70000, '600hPa': 60000,
    '500hPa':  50000,  '400hPa': 40000, '300hPa': 30000, '250hPa': 25000,
    '200hPa':  20000,  '150hPa': 15000, '100hPa': 10000, '70hPa':  7000,
    '50hPa':   5000,   '30hPa':  3000,  '20hPa':  2000
}

# Load and filter grib data to get regional temperature
# at the specified isobaric level
def parse_data(filepath):
    # Load the grib files into an xarray dataset
    ds = xr.open_dataset(filepath, engine='pynio')
    # Print information on data variables
    # print(ds.keys())
    # Rename the temperature variable for clarity
    # See DEF_VARIABLES above to lookup variable names
    ds = ds.rename({'TMP_P0_L100_GLL0': 'temperature'})
    # Get only the temperature values at isobaric levels
    # to significantly reduce the volume of data right away,
    # otherwise converting to a dataframe will take a long time
    ds = ds.get('temperature')
    # Convert the xarray dataset to a dataframe
    df = ds.to_dataframe()
    # Retrieve isobaric level values
    isblevels = df.index.get_level_values('lv_ISBL0')
    # Filter to a specific isobaric level:
    # 20 hPa (2000 pascal)
    df = df.loc[(isblevels == isobaric_levels['20hPa'])]
    # Perform an initial coarse filter on the global dataframe
    # by limiting the data to the area's bounding box,
    # thereby reducing the total processing time of the `precise_geo_filter`
    df = coarse_geo_filter(df, AREA)
    # Perform the precise filter to remove data outside of the shapefile area
    df = precise_geo_filter(df, AREA)
    # Trim the data to just the lat, lon, and temperature columns
    df_viz = df.loc[:, ['latitude','longitude','temperature']]
    # Convert from Kelvin to Celsius
    df_viz['temperature'] = df_viz['temperature'] - 273.15
    return df_viz

# Visualize the data
def plot_data(data):
    x = data['longitude'].values
    y = data['latitude'].values
    color = data['temperature'].values
    plt.scatter(
        x,
        y,
        c=color,
        s=10,
        cmap='coolwarm',
        linewidths=0.1
    )
    plt.title('Temperature (C) at 20 hPa')
    plt.colorbar()
    plt.show()

if __name__ == '__main__':
    parser = argparse.ArgumentParser(
        description='Extract regional data from a GRIB file at a single vertical level'
    )
    parser.add_argument(
        'filepath', type=str, help='The path to the Upper-Air bundle GRIB file to open'
    )
    args = parser.parse_args()
    data = parse_data(args.filepath)
    plot_data(data)
