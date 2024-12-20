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


def get_file_list(export_id: str) -> list[str]:
    resp = get(f"{base_url}/{export_id}")
    if resp.status_code == 404:
        raise Exception("Unknown export id")

    return resp.json()["files"]


def download_file(export_id: str, path: str, local_path: str) -> bool:
    prefix = Path(local_path)
    with get(f"{base_url}/{export_id}/{path}", allow_redirects=True, stream=True) as resp:
        if resp.status_code == 404:
            return False
        download_path = prefix / path
        if download_path.exists():
            return True

        try:
            download_path.parent.mkdir(parents=True, exist_ok=True)
            with download_path.open("rb") as f:
                for chunk in resp.iter_content(chunk_size=8192):
                    f.write(chunk)
        except BaseException:
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
