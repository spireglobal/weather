import argparse
import os
from urllib.parse import urljoin

import requests

HOST = 'https://api.wx.spire.com'
API_KEY = os.getenv('spire-api-key')


def download_complete_issuance(api_key, output_directory=None):
    # Build the URL, add the headers and query parameters.
    url = urljoin(HOST, '/forecast/file')
    params = {'bundles': 'basic', 'time_bundle': 'medium_range_high_freq'}
    headers = {'spire-api-key': api_key}
    response = requests.get(url, headers=headers, params=params)

    json_response = response.json()
    if 'files' not in json_response:
        raise Exception('Response did not contain a files element', json_response)

    file_list = json_response['files']

    expected_number_of_files = 49
    if len(file_list) == expected_number_of_files:
        for forecast in file_list:
            if output_directory:
                output_file_path = os.path.join(output_directory, forecast)
            else:
                output_file_path = forecast

            print('Downloading: %s to %s' % (forecast, output_file_path))

            # Retrieve the file content
            single_file_url = urljoin(HOST, '/forecast/file/') + forecast
            download_file_response = requests.get(single_file_url, headers=headers, allow_redirects=True)

            # Save the file content to the output directory.
            with open(output_file_path, 'wb') as f:
                f.write(download_file_response.content)
    else:
        print(f'There are {len(file_list)} files and we were expecting {expected_number_of_files}')


if __name__ == '__main__':
    if not API_KEY:
        raise Exception('API_KEY environment variable is not set.')

    parser = argparse.ArgumentParser(description='Download all forecast files')
    parser.add_argument('--output_directory', type=str,
                        help='The directory to download the files')

    args = parser.parse_args()
    download_complete_issuance(API_KEY, args.output_directory)
