from osgeo.ogr import Geometry, wkbPoint
# Only one OGR point needs to be created,
# since each call to `OGR_POINT.AddPoint`
# in the `check_point_in_area` function
# will reset the variable
OGR_POINT = Geometry(wkbPoint)

def coarse_geo_filter(df, AREA):
	"""
	Perform an initial coarse filter on the dataframe
	based on the extent (bounding box) of the specified area
	"""
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
	return df

def precise_geo_filter(df, AREA):
	"""
	Perform a precise filter on the dataframe
	to check if each point is inside of the shapefile area
	"""
	# Create a new tuple column in the dataframe of lat/lon points
	df['point'] = list(zip(df['latitude'], df['longitude']))
	# Create a new boolean column in the dataframe, where each value represents
	# whether the row's lat/lon point is contained in the shpfile area
	map_func = lambda latlon: check_point_in_area(latlon, AREA)
	df['inArea'] = df['point'].map(map_func)
	# Remove point locations that are not within the shpfile area
	df = df.loc[(df['inArea'] == True)]
	return df

def check_point_in_area(latlon, AREA):
	"""
	Return a boolean value indicating whether
	the specified point is inside of the shapefile area
	"""
	# Initialize flag
	point_in_area = False
	# Parse coordinates and convert to floats
	lat = float(latlon[0])
	lon = float(latlon[1])
	# Set the point geometry
	OGR_POINT.AddPoint(lon, lat)
	# Check if the point is in any of the shpfile's features
	for i in range(AREA.GetFeatureCount()):
		feature = AREA.GetFeature(i)
		if feature.geometry().Contains(OGR_POINT):
			# This point is within a feature
			point_in_area = True
			# Break out of the loop
			break
	# Return flag indicating whether point is in the area
	return point_in_area
