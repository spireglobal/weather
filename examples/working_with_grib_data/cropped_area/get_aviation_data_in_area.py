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

# Load the shapefile area
driver = ogr.GetDriverByName('ESRI Shapefile')
shpfile = driver.Open('shpfile/france.shp')
AREA = shpfile.GetLayer()

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
    ds = ds.rename({'CAT_P0_L102_GLL0': 'turbulence'})
    # Get only the turbulence values at flight levels
    # to significantly reduce the volume of data right away,
    # otherwise converting to a dataframe will take a long time
    ds = ds.get('turbulence')
    # Convert the xarray dataset to a dataframe
    df = ds.to_dataframe()
    # Retrieve flight level values
    flightlevels = df.index.get_level_values('lv_AMSL0')
    # Filter to a specific flight level:
    # FL100 = 10000 feet = 3048 meters
    df = df.loc[(flightlevels == 3048)]
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
    # Trim the data to just the lat, lon, and turbulence columns
    df_viz = df.loc[:, ['latitude','longitude','turbulence']]
    return df_viz

# Visualize the data
def plot_data(data):
    x = data['longitude'].values
    y = data['latitude'].values
    color = data['turbulence'].values
    plt.scatter(
        x,
        y,
        c=color,
        s=10,
        cmap='Spectral_r',
        edgecolors='gray',
        linewidths=0.1
    )
    plt.title('Clear-Air Turbulence % at FL100')
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