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

import os
import pickle
import sys
import time
import ee
import pandas as pd

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from utils.utils import initialize_gee, get_feature_collection

# PARAMETERS
POLYGONS_FEATURE_COLLECTION = 'projects/ee-ronnyale/assets/random_sample_1000_filtered_polygons'
PROJECT_TO_SAVE_ASSETS = 'projects/ee-ronnyale/assets/'
DATA_OUTPUT_DIR = 'data_out/'

initialize_gee()

# Import LEAFtoolbox modules
module_path = os.path.abspath(os.path.join('..'))
print(module_path)
if module_path not in sys.path:
    sys.path.append(module_path)

from leaftoolbox import LEAF
from leaftoolbox import SL2PV0 

# Start the process
batch_size = 20
polygon_collection = get_feature_collection(POLYGONS_FEATURE_COLLECTION)
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
        pickle_filename = f'{DATA_OUTPUT_DIR}time_series_{label}_batch_{start_index}.pkl'

        # Check if pkl file for the batch already exists
        if os.path.exists(pickle_filename):
            print(f'Batch {start_index} for {label} already processed and saved. Skipping...')
            continue
        batch = polygon_collection.toList(batch_size, start_index)
        batch_fc = ee.FeatureCollection(batch)
        batch_asset_id = f'{PROJECT_TO_SAVE_ASSETS}_temp_batch_{label}_{start_index}'
        task = ee.batch.Export.table.toAsset(
            collection = batch_fc,
            description = f'export_batch_{label}_{start_index}',
            assetId = batch_asset_id
        )
        print(f'Exporting batch {start_index} for {label} to GEE')
        task.start()

        # Avoid running if asset is not ready yet
        while task.status()['state'] in ['READY', 'RUNNING']:
            time.sleep(10)

        start_time = time.time()
        sites_dictionary = LEAF.sampleSites(
            [batch_asset_id],
            imageCollectionName = image_collection_name,
            algorithm = SL2PV0,
            variableName = "Surface_Reflectance",
            maxCloudcover = 90,
            outputScaleSize = 30,
            inputScaleSize = 30,
            bufferSpatialSize = 0,
            numPixels = 100
        )
        end_time = time.time()
        execution_time = end_time - start_time
        print(f'Execution time for batch {start_index} with {label}: {execution_time} seconds')

        # Extract and process results
        outer_key = list(sites_dictionary.keys())[0]
        first_item = sites_dictionary[outer_key]
        batch_results = []

        for item in range(len(first_item)):
            df = first_item[item]['leaftoolbox.SL2PV0']
            df['site'] = first_item[item]['feature']['wllst__']
            batch_results.append(df)

        # Combine batch results
        combined_df = pd.concat(batch_results, ignore_index = True)
        with open(pickle_filename, 'wb') as file:
            pickle.dump(combined_df, file)
        
        print(f'Batch {start_index} for {label} saved to {pickle_filename}')
