"""
Run LEAF toolbox sampler

This runs the LEAF toolbox sampler over the polygons for
the required image collections products. It performs the
following steps:

1. Initializes the GEE API
2. Divides the asset into batches
3. Export each batch as an asset
4. Runs the sampler for each bacth
5. Extracts the results and save them as pkl files

Parameters:

- polygon_collection: The feature collection of polygons from 
  the specified site.
- total_polygons: The total number of polygons in the feature
  collection.
- image_collections: A list of dictionaries containing the 
  image collection names and labels.
- batch_asset_id: The ID for the temporary batch asset in GEE.

Outputs:
- Pickle files: One pickle file per image collection and batch,
  saved in the current directory.

Usage:
- Run the script with the specified site and batch_size.
- The script will automatically handle the processing of 
  the batches and save the results.
- If a batch has already been processed, it will skip that
  batch to avoid duplication.

Author: Ronny A. Hernández Mora
"""

import json
import os
import pickle
import sys
import time

import ee
import matplotlib.pyplot as plt
import pandas as pd

from utils.utils import initialize_gee, get_feature_collection

# Start the process
initialize_gee()
batch_size = 20
polygon_collection = get_feature_collection(
    'projects/ee-ronnyale/assets/random_sample_1000_filtered_polygons')
total_polygons = polygon_collection.size().getInfo()

# Products to be processed
image_collections = [
    {"name": "LANDSAT/LC08/C02/T1_L2", "label": "LC08"},
    {"name": "LANDSAT/LC09/C02/T1_L2", "label": "LC09"},
    {"name": "COPERNICUS/S2_SR_HARMONIZED", "label": "S2"}        
]

for collection in image_collections:
    image_collection_name = collection["name"]
    label = collection["label"]

    # Process each batch
    for start_index in range(0, total_polygons, batch_size):
        pickle_filename = f'time_series_{label}_batch_{start_index}.pkl'

        # Check if pkl file for the batch already exists
        if os.path.exists(pickle_filename):
            print(f'Batch {start_index} for {label} already processed and saved. Skipping...')
            continue
        batch = polygon_collection.toList(batch_size, start_index)
        batch_fc = ee.FeatureCollection(batch)
        batch_asset_id = f'projects/ee-ronnyale/assets/temp_batch_{lable}_{start_index}'
        task = ee.batch.Export.table.toAsset(
            collection = batch_fc,
            description = f'export_batch_{label}_{start_index}',
            assetId = batch_asset_id
        )
        task.start()

        

