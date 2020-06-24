"""
Extract swell wave height from Maritime Waves GRIB messages

This program extracts wave data from a GRIB file and writes it to a CSV
"""
import argparse
import xarray as xr

# DEF_VARIABLES = (
#     'WVDIR_P0_L101_GLL0', # Direction of wind waves
#     'WVHGT_P0_L101_GLL0', # Significant height of wind waves
#     'WVPER_P0_L101_GLL0', # Mean period of wind waves
#     'SWDIR_P0_L101_GLL0', # Direction of Swell Waves
#     'SWELL_P0_L101_GLL0', # Significant height of swell waves
#     'SWPER_P0_L101_GLL0', # Mean period of swell waves
# )

# Load and filter grib data to get global swell wave height
def parse_data(filepath):
    # Load the grib file into an xarray dataset
    ds = xr.open_dataset(filepath, engine='pynio')
    # Print information on data variables
    # print(ds.keys())
    # Convert the xarray dataset to a dataframe
    df = ds.to_dataframe()
    # Get longitude values from index
    lons = df.index.get_level_values('lon_0')
    # Define mapping of longitude range from (0 to 360) to (-180 to 180)
    maplon = lambda lon: (lon - 360) if (lon > 180) else lon
    # Create new longitude and latitude columns in the dataframe
    df['longitude'] = lons.map(maplon)
    df['latitude'] = df.index.get_level_values('lat_0')
    # Rename the data field for clarity (see DEF_VARIABLES above)
    df['swell_height'] = df['SWELL_P0_L101_GLL0']
    # Trim the data to just the lat, lon, and swell_height columns
    df_trim = df.loc[:, ['latitude','longitude','swell_height']]
    return df_trim

if __name__ == '__main__':
    parser = argparse.ArgumentParser(
        description='Get global ocean wave height from a GRIB file'
    )
    parser.add_argument(
        'filepath', type=str, help='The path to the Maritime Waves bundle GRIB file to open'
    )
    args = parser.parse_args()
    data = parse_data(args.filepath)
    # Write all of the columns to CSV, ignoring the index values
    data.to_csv('global_swell_wave_height.csv', index=False)
