"""
Download data file.

There are 3 datasets needed to derive the Indicators
from Satellite Observations of Vegetation Essential
Climate Variables Reclaimed Well and Mine Sites in 
Alberta, Canada.

The datasets are:

 - Land-use/Land-cover Classification of Alberta, 
   Derived from 2020 Sentinel-2 Multispectral Data.
   From the Alberta Energy Regulator (AER)
 - Wall-to-Wall Human Footprint Inventory 2021 from the
   Alberta Biodiversity Monitoring Institute (ABMI)
 - Canadian National Fire Database (CNFDB) from the
   Natural Resources Canada (NRCan)

This file will download the zip files directly from
each of the institutions and unzip them in a data folder.

The data will be processed to create assets in GEE.

Author: Ronny A. Hernández Mora
"""

import os
import requests
from zipfile import ZipFile
from tqdm import tqdm

def download_and_extract(url, dest_folder):
    # Create the destination directory if it doesn't exist
    if not os.path.exists(dest_folder):
        os.makedirs(dest_folder)

    # Extract the filename from the URL
    filename = os.path.join(dest_folder, os.path.basename(url))

    # Start the download with a progress bar
    response = requests.get(url, stream=True)
    total_size = int(response.headers.get('content-length', 0))
    block_size = 1024  # 1 Kilobyte

    with open(filename, 'wb') as file, tqdm(
        desc=filename,
        total=total_size,
        unit='B',
        unit_scale=True,
        unit_divisor=1024,
    ) as bar:
        for data in response.iter_content(block_size):
            file.write(data)
            bar.update(len(data))

    print(f"\nFile saved as {filename}")

    # Unzip file
    if filename.endswith('.zip'):
        print(f"Unzipping {filename}...")
        with ZipFile(filename, 'r') as zip_ref:
            zip_ref.extractall(dest_folder)
        print(f"Extracted {filename} to {dest_folder}")

# Loop through each URL and download/extract the data
urls = [
    'https://ftp-public.abmi.ca/GISData/HumanFootprint/2021/HFI2021.gdb.zip',
    'https://static.ags.aer.ca/files/document/DIG/DIG_2021_0019.zip',
    'https://cwfis.cfs.nrcan.gc.ca/downloads/nfdb/fire_poly/current_version/NFDB_poly.zip'
]

for url in urls:
    download_and_extract(url, 'data_check')
