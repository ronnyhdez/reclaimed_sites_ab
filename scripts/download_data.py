import os
import requests
from zipfile import ZipFile

# Define the URL and the destination directory
# url = 'https://ftp-public.abmi.ca/GISData/HumanFootprint/2021/HFI2021.gdb.zip'
url = 'https://ftp-public.abmi.ca/GISData/HumanFootprint/2021/HFIeOSA_2021.gdb.zip'
dest_folder = 'data_in'

# Create the destination directory if it doesn't exist
if not os.path.exists(dest_folder):
    os.makedirs(dest_folder)

# Extract the filename from the URL
filename = os.path.join(dest_folder, os.path.basename(url))

# Download the file
print(f"Downloading {url}...")
response = requests.get(url)
response.raise_for_status()  # Check if the download was successful

# Save the file to the destination directory
with open(filename, 'wb') as file:
    file.write(response.content)

print(f"File saved as {filename}")

# Optionally, if it's a zip file, you can unzip it
if filename.endswith('.zip'):
    with ZipFile(filename, 'r') as zip_ref:
        zip_ref.extractall(dest_folder)
    print(f"Extracted {filename} to {dest_folder}")
