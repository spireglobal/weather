"""
Example of how to use the Spire Weather File API to download all GRIB files for a particular product
bundle and time bundle. This code is set up to download all data files once the full forecast has
finished rather than individual files as they populate the API.

"""
import argparse
import os
from urllib.parse import urljoin

import requests

HOST = 'https://api.wx.spire.com'
API_KEY = os.getenv('spire-api-key')


def download_complete_issuance(api_key, output_directory=None):
    # Build the URL, add the headers and query parameters.
    url = urljoin(HOST, '/forecast/file')
    params = {'bundles': 'basic', 'time_bundle': 'medium_range_std_freq'}
    headers = {'spire-api-key': api_key}
    response = requests.get(url, headers=headers, params=params)

    json_response = response.json()
    if 'files' not in json_response:
        raise Exception('Response did not contain a files element', json_response)

    file_list = json_response['files']

    # The medium range, standard time frequency bundle contains data for 29 lead times (or steps)
    # representing forecasts at six hour intervals from 0 to 168 hours.
    # Only perform the download once the complete forecast dataset is available.
    expected_number_of_files = 29
    if len(file_list) == expected_number_of_files:
        for forecast in file_list:
            if output_directory:
                output_file_path = os.path.join(output_directory, forecast)
            else:
                output_file_path = forecast

            print('Downloading: %s to %s' % (forecast, output_file_path))

            # Retrieve the file content.
            # NB: No checking is performed to skip downloading previously downloaded data files.
            single_file_url = urljoin(HOST, '/forecast/file/') + forecast
            download_file_response = requests.get(single_file_url, headers=headers, allow_redirects=True)

            # Save the file content to the output directory.
            with open(output_file_path, 'wb') as f:
                f.write(download_file_response.content)
    else:
        print(f'There are {len(file_list)} files and we were expecting {expected_number_of_files}')


if __name__ == '__main__':
    if not API_KEY:
        raise Exception('spire-api-key environment variable is not set.')

    parser = argparse.ArgumentParser(description='Download all forecast files')
    parser.add_argument('--output_directory', type=str,
                        help='The directory to download the files into')

    args = parser.parse_args()
    download_complete_issuance(API_KEY, args.output_directory)
