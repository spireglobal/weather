# Spire Weather

## Dependencies 

This project requires the following libraries.
    
    - pyNIO
    - pygrib
    - requests
    - tabulate
    
    
### API Examples
    
    env spire-api-key='xxxxxxxxxxxxxxxxx' python examples/point_api_example.py --lat 10 --lon 10
    env spire-api-key='xxxxxxxxxxxxxxxxx' python examples/point_api_basic_maritime_valid_time_filter.py --lat 10 --lon 10
    env spire-api-key='xxxxxxxxxxxxxxxxx' python examples/point_api_basic_specify_bundle.py --lat 10 --lon 10 --bundles 'basic,agricultural'
    env spire-api-key='xxxxxxxxxxxxxxxxx' python examples/point_api_precip_example.py --lat 10 --lon 10


### Working with GRIB data

    python examples/working_with_grib_data/get_data_from_grib_file_pygrib.py sof-d.20190920.t00z.0p125.basic.global.f006.grib2 --lat 50.000 --lon 51 
    python examples/working_with_grib_data/get_data_from_grib_file_pynio.py sof-d.20190920.t00z.0p125.basic.global.f006.grib2 --lat 50.000 --lon 51 
