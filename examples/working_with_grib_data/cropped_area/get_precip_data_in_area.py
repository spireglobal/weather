"""
Extract accumulated, regional values from Basic GRIB messages

This program extracts precipitation data from 2 GRIB files,
and takes the difference to get fixed-interval accumulations.
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

# Load and filter grib data to get regional precipitation
def parse_data(filepath1, filepath2):
    # Load the grib files into xarray datasets
    ds1 = xr.open_dataset(filepath1, engine='pynio')
    ds2 = xr.open_dataset(filepath2, engine='pynio')
    # Print information on data variables
    # print(ds1.keys())
    # Convert the xarray datasets to dataframes
    df1 = ds1.to_dataframe()
    df2 = ds2.to_dataframe()
    # Create a new dataframe with the same lat/lon index
    df = pd.DataFrame(index=df1.index)
    # Since the grib data is forecast-total accumulated precipitation,
    # subtract the older value from the newer one to get fixed-interval values
    df['precip'] = df2['APCP_P8_L1_GLL0_acc'] - df1['APCP_P8_L1_GLL0_acc']
    # Perform an initial coarse filter on the global dataframe
    # by limiting the data to the area's bounding box,
    # thereby reducing the total processing time of the `precise_geo_filter`
    df = coarse_geo_filter(df, AREA)
    # Perform the precise filter to remove data outside of the shapefile area
    df = precise_geo_filter(df, AREA)
    # Trim the data to just the lat, lon, and precipitation columns
    df_viz = df.loc[:, ['latitude','longitude','precip']]
    # Convert from millimeters to inches
    # df_viz['precip'] = df_viz['precip'] * 0.0393701
    return df_viz

# Visualize the data
def plot_data(data):
    x = data['longitude'].values
    y = data['latitude'].values
    color = data['precip'].values
    plt.scatter(
        x,
        y,
        c=color,
        s=10,
        cmap='Blues',
        edgecolors='gray',
        linewidths=0.1
    )
    plt.title('Precipitation (mm)')
    plt.colorbar()
    plt.show()

if __name__ == '__main__':
    parser = argparse.ArgumentParser(
        description='Get fixed-interval precipitation values within a region by differencing 2 GRIB files'
    )
    parser.add_argument(
        'filepath1', type=str, help='The path to the earlier Basic bundle GRIB file to open'
    )
    parser.add_argument(
        'filepath2', type=str, help='The path to the later Basic bundle GRIB file to open'
    )
    args = parser.parse_args()
    data = parse_data(args.filepath1, args.filepath2)
    plot_data(data)
