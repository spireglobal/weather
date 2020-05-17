"""
Extract regional values from an Aviation GRIB file at one vertical level

This program extracts clear-air turbulence data from a GRIB file
at a single vertical (flight) level. It then crops the data
to the horizontal area of a provided shapefile.
"""
import argparse
import xarray as xr
import pandas as pd
import matplotlib.pyplot as plt
from osgeo import ogr
from math import atan2, pi, sqrt

# Load the shapefile area
driver = ogr.GetDriverByName('ESRI Shapefile')
shpfile = driver.Open('shpfile/italy.shp')
AREA = shpfile.GetLayer()

# Compute the wind speed
def wind_speed_from_u_v(row):
    u = row['eastward-wind']
    v = row['northward-wind']
    return sqrt(pow(u, 2) + pow(v, 2))

# Compute the wind direction
def wind_direction_from_u_v(row):
    """
    Meteorological wind direction
      90° corresponds to wind from east,
      180° from south
      270° from west
      360° wind from north.
      0° is used for no wind.
    """
    u = row['eastward-wind']
    v = row['northward-wind']
    if (u, v) == (0.0, 0.0):
        return 0.0
    else:
        return (180.0 / pi) * atan2(u, v) + 180.0

# Check if point is inside of shapefile area
def area_filter(latlon):
    # Initialize flag
    point_in_area = False
    # Parse coordinates and convert to floats
    lat = float(latlon[0])
    lon = float(latlon[1])
    # Create a point geometry
    point = ogr.Geometry(ogr.wkbPoint)
    point.AddPoint(lon, lat)
    # Check if the point is in any of the shpfile's features
    for i in range(AREA.GetFeatureCount()):
        feature = AREA.GetFeature(i)
        if feature.geometry().Contains(point):
            # This point is within a feature
            point_in_area = True
            # Break out of the loop
            break
    # Return flag indicating whether point is in the area
    return point_in_area

# Load, filter, and process grib data
# to get wind speed within a region
def parse_data(filepath):
    # Load the grib files into an xarray dataset
    ds = xr.open_dataset(filepath, engine='pynio')
    # Print information on data variables
    # print(ds.keys())
    # Rename the wind variables for clarity
    ds = ds.rename({'UGRD_P0_L103_GLL0': 'eastward-wind'})
    ds = ds.rename({'VGRD_P0_L103_GLL0': 'northward-wind'})
    # Get only the wind values to reduce the volume of data,
    # otherwise converting to a dataframe will take a long time
    ds = ds.get(['eastward-wind','northward-wind'])
    # Convert the xarray dataset to a dataframe
    df = ds.to_dataframe()
    # Get longitude values from index
    lons = df.index.get_level_values('lon_0')
    # Map longitude range from (0 to 360) into (-180 to 180)
    maplon = lambda lon: (lon - 360) if (lon > 180) else lon
    # Create new longitude and latitude columns in the dataframe
    df['longitude'] = lons.map(maplon)
    df['latitude'] = df.index.get_level_values('lat_0')
    # Get the area's bounding box
    extent = AREA.GetExtent()
    minlon = extent[0]
    maxlon = extent[1]
    minlat = extent[2]
    maxlat = extent[3]
    # Perform an initial coarse filter on the global dataframe
    # by limiting the data to the area's bounding box,
    # thereby reducing the total processing time of the `area_filter`
    latfilter = ((df['latitude'] >= minlat) & (df['latitude'] <= maxlat))
    lonfilter = ((df['longitude'] >= minlon) & (df['longitude'] <= maxlon))
    # Apply filters to the dataframe
    df = df.loc[latfilter & lonfilter]
    # Create tuple column of latitude and longitude points
    df['point'] = list(zip(df['latitude'], df['longitude']))
    # Create boolean column for whether the shpfile area contains the point
    df['inArea'] = df['point'].map(area_filter)
    # Crop point locations that are not within the shpfile area
    df = df.loc[(df['inArea'] == True)]
    # Compute the wind speed
    df['wind-speed'] = df.apply (lambda row: wind_speed_from_u_v(row), axis=1)
    # Compute the wind direction
    df['wind-dir'] = df.apply (lambda row: wind_direction_from_u_v(row), axis=1)
    # Trim the data to just the lat, lon, and turbulence columns
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
        # edgecolors='gray',
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
