"""
Extract regional values from an Basic GRIB file at one vertical level

This program extracts wind speed data from a GRIB file.
It then crops the data to the area of a provided shapefile.
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
#     'TMP_P0_L103_GLL0',        # Temperature
#     'DPT_P0_L103_GLL0',        # Dew point temperature
#     'RH_P0_L103_GLL0',         # Relative humidity
#     'UGRD_P0_L103_GLL0',       # U-component of wind
#     'VGRD_P0_L103_GLL0',       # V-component of wind
#     'GUST_P0_L1_GLL0',         # Wind speed (gust)
#     'PRMSL_P0_L101_GLL0',      # Pressure reduced to MSL
#     'TMAX_P8_L103_GLL0_max',   # Maximum temperature
#     'TMIN_P8_L103_GLL0_min',   # Minimum temperature
#     'APCP_P8_L1_GLL0_acc',     # Total precipitation
#     'lat_0',                   # latitude
#     'lon_0',                   # longitude
# )

# Load, filter, and process grib data
# to get wind speed within a region
def parse_data(filepath):
    # Load the grib files into an xarray dataset
    ds = xr.open_dataset(filepath, engine='pynio')
    # Print information on data variables
    # print(ds.keys())
    # Rename the wind variables for clarity
    # See DEF_VARIABLES above to lookup variable names
    ds = ds.rename({'UGRD_P0_L103_GLL0': 'eastward-wind'})
    ds = ds.rename({'VGRD_P0_L103_GLL0': 'northward-wind'})
    # Get only the wind values to reduce the volume of data,
    # otherwise converting to a dataframe will take a long time
    ds = ds.get(['eastward-wind','northward-wind'])
    # Convert the xarray dataset to a dataframe
    df = ds.to_dataframe()
    # Perform an initial coarse filter on the global dataframe
    # by limiting the data to the area's bounding box,
    # thereby reducing the total processing time of the `precise_geo_filter`
    df = coarse_geo_filter(df, AREA)
    # Perform the precise filter to remove data outside of the shapefile area
    df = precise_geo_filter(df, AREA)
    # Compute the wind speed
    ws_func = lambda row: wind_speed_from_u_v(row['eastward-wind'], row['northward-wind'])
    df['wind-speed'] = df.apply(ws_func, axis=1)
    # Compute the wind direction
    wd_func = lambda row: wind_direction_from_u_v(row['eastward-wind'], row['northward-wind'])
    df['wind-dir'] = df.apply(wd_func, axis=1)
    # Trim the data to just the lat, lon, and wind speed columns
    df_viz = df.loc[:, ['latitude','longitude','wind-speed','wind-dir']]
    return df_viz

# Visualize the data
def plot_data(data):
    x = data['longitude'].values
    y = data['latitude'].values
    color = data['wind-speed'].values
    plt.scatter(
        x,
        y,
        c=color,
        s=10,
        cmap='Spectral_r',
        linewidths=0.1
    )
    plt.title('Wind Speed (m/s)')
    plt.colorbar()
    plt.show()

if __name__ == '__main__':
    parser = argparse.ArgumentParser(
        description='Extract regional U-wind and V-wind data from a GRIB file to compute wind speed and direction'
    )
    parser.add_argument(
        'filepath', type=str, help='The path to the Basic bundle GRIB file to open'
    )
    args = parser.parse_args()
    data = parse_data(args.filepath)
    plot_data(data)
