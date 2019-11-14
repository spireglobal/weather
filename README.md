# Spire Weather

This repository hosts some sample programs to help you get up and running with Spire Weather APIs.

Don't hesitate to consult our full API documentation as you go through these examples:

https://developers.wx.spire.com/


## Dependencies 

The example programs require the following libraries in a Python 3.x environment:
    
    - pyNIO
    - pygrib
    - requests
    - tabulate
    
    
### API Examples

Sample syntax for the examples under Bash on linux systems is:

    env spire-api-key='xxxxxxxxxxxxxxxxx' python examples/point_api_example.py --lat 10 --lon 10
    env spire-api-key='xxxxxxxxxxxxxxxxx' python examples/point_api_basic_maritime_valid_time_filter.py --lat 10 --lon 10
    env spire-api-key='xxxxxxxxxxxxxxxxx' python examples/point_api_basic_specify_bundle.py --lat 10 --lon 10 --bundles 'basic,agricultural'
    env spire-api-key='xxxxxxxxxxxxxxxxx' python examples/point_api_precip_example.py --lat 10 --lon 10

Here you would use the Spire Weather API key provided to you were granted access to the APIs.


### Working with GRIB data

These examples require that you have already downloaded one or more GRIB files from the File API and replace the filename below accordingly.

    python examples/working_with_grib_data/get_data_from_grib_file_pygrib.py sof-d.20190920.t00z.0p125.basic.global.f006.grib2 --lat 50.0 --lon 51.0
    python examples/working_with_grib_data/get_data_from_grib_file_pynio.py sof-d.20190920.t00z.0p125.basic.global.f006.grib2 --lat 50.0 --lon 51.0
