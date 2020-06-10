"""
Extract regional values from an Aviation GRIB file at one vertical level

This program extracts wind speed data from a GRIB file
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

# DEF_VARIABLES = (
#     'TMP_P0_L102_GLL0',     # Temperature
#     'RH_P0_L102_GLL0',      # Relative humidity
#     'TIPD_P0_L100_GLL0',    # Total icing potential diagnostic
#     'TIPD_P0_L102_GLL0',    # Total icing potential diagnostic
#     'UGRD_P0_L6_GLL0',      # U-component of wind
#     'UGRD_P0_L102_GLL0',    # U-component of wind (vertical levels)
#     'VGRD_P0_L6_GLL0',      # V-component of wind
#     'VGRD_P0_L102_GLL0',    # V-component of wind (vertical levels)
#     'HGT_P0_L6_GLL0',       # Geopotential height
#     'VIS_P0_L1_GLL0',       # Visibility
#     'CAT_P0_L102_GLL0',     # Clear air turbulence
#     'lv_AMSL2',             # Specific altitude above mean sea level
#     'lv_ISBL1',             # Isobaric surface
#     'lat_0',                # latitude
#     'lon_0',                # longitude
#     'lv_AMSL0',             # Specific altitude above mean sea level
# )

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

# Create a dictionary for flight levels
# and corresponding values in meters
flight_levels = {
    'FL100': 3048,
    'FL110': 3352,
    'FL120': 3657,
    'FL130': 3962,
    'FL140': 4267,
    'FL150': 4572,
    'FL160': 4876,
    'FL170': 5181,
    'FL180': 5486,
    'FL190': 5791,
    'FL200': 6096,
    'FL210': 6400,
    'FL220': 6705,
    'FL230': 7010,
    'FL240': 7315,
    'FL250': 7620,
    'FL260': 7924,
    'FL270': 8229,
    'FL280': 8534,
    'FL290': 8839,
    'FL300': 9144,
    'FL310': 9448,
    'FL320': 9753,
    'FL330': 10058,
    'FL340': 10363,
    'FL350': 10668,
    'FL360': 10972,
    'FL370': 11277,
    'FL380': 11582,
    'FL390': 11887,
    'FL400': 12192,
    'FL410': 12496,
    'FL420': 12801,
    'FL430': 13106,
    'FL440': 13411,
    'FL450': 13716
}

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

# Load and filter grib data to get clear-air turbulence
# within a region at the specified flight level
def parse_data(filepath):
    # Load the grib files into an xarray dataset
    ds = xr.open_dataset(filepath, engine='pynio')
    # Print information on data variables
    # print(ds.keys())
    # Rename the clear-air turbulence variable for clarity
    # See DEF_VARIABLES above to lookup variable names
    # Rename the wind variables for clarity
    ds = ds.rename({'UGRD_P0_L102_GLL0': 'eastward-wind'})
    ds = ds.rename({'VGRD_P0_L102_GLL0': 'northward-wind'})
    # Get only the wind values to reduce the volume of data,
    # otherwise converting to a dataframe will take a long time
    ds = ds.get(['eastward-wind','northward-wind'])
    # Convert the xarray dataset to a dataframe
    df = ds.to_dataframe()
    # Retrieve flight level values
    flmeters = df.index.get_level_values('lv_AMSL0')
    # Filter to a specific flight level,
    # using the lookup dictionary from above
    df = df.loc[(flmeters == flight_levels['FL360'])]
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
    # Trim the data to just the lat, lon, and wind speed columns
    df_viz = df.loc[:, ['latitude','longitude','wind-speed', 'wind-dir']]
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
    plt.title('Wind Speed at FL360')
    plt.colorbar()
    plt.show()

if __name__ == '__main__':
    parser = argparse.ArgumentParser(
        description='Extract regional data from a GRIB file at a single vertical level'
    )
    parser.add_argument(
        'filepath', type=str, help='The path to the Aviation bundle GRIB file to open'
    )
    args = parser.parse_args()
    data = parse_data(args.filepath)
    plot_data(data)
