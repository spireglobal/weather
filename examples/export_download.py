"""
This script will download all files from a Spire data export in parallel.

For more detail on Spire weather archive requests and retrievals see
our developer documentation and getting started guides:
https://developers.wx.spire.com/swagger_ui/index.html#/Archive%20Data/get_archive_file_list
https://developers.wx.spire.com/getting-started.pdf

To use, first install requests from pip:
    pip install requests

Then insert your export id below and run the script.
"""

from pathlib import Path
from concurrent.futures import ThreadPoolExecutor

from requests import get


# The export id given to you by Spire
export_id = "<insert export id>"

base_url = "https://api.wx.spire.com/export"

# The number of download workers
parallelism = 8

# The local path where files will be downloaded
prefix = "."

# Enable extra logging
debug = False


def debug_log(msg: str) -> None:
    if debug:
        print(msg)


def get_file_list(export_id: str) -> list[str]:
    resp = get(f"{base_url}/{export_id}")
    if resp.status_code == 404:
        raise Exception("Unknown export id")

    return resp.json()["files"]


def download_file(export_id: str, path: str, local_path: str) -> bool:
    prefix = Path(local_path)
    url = f"{base_url}/{export_id}/{path}"

    debug_log(f"Getting {url}...")
    with get(url, allow_redirects=True, stream=True) as resp:
        if resp.status_code == 404:
            debug_log("Not found")
            return False

        download_path = prefix / path
        debug_log(f"Checking {download_path}")
        if download_path.exists():
            debug_log(f"Skipping {download_path}")
            return True

        debug_log(f"Saving {download_path}")
        try:
            download_path.parent.mkdir(parents=True, exist_ok=True)
            with download_path.open("wb") as f:
                for chunk in resp.iter_content(chunk_size=8192):
                    f.write(chunk)
        except BaseException as e:
            debug_log(f"Download failed with {str(e)}")
            if download_path.exists():
                download_path.unlink()
                return False

    return True


if __name__ == "__main__":
    files = get_file_list(export_id)
    print(f"Downloading {len(files)} files...")
    with ThreadPoolExecutor(max_workers=parallelism) as pool:
        results = pool.map(lambda f: download_file(export_id, f, prefix), files)
        for i, result in enumerate(results):
            if not result:
                print(f"Failed to download {files[i]}")
            else:
                print(files[i])

        print("done")
