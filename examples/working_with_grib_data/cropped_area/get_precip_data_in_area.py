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
from osgeo import ogr

# Load the shapefile area
driver = ogr.GetDriverByName('ESRI Shapefile')
shpfile = driver.Open('shpfile/italy.shp')
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
    # Drop point locations that are not within the shpfile area
    df = df.loc[(df['inArea'] == True)]
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
