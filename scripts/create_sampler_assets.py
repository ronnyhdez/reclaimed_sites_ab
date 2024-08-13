"""
Create the assets to be used in the LEAFtoolbox sampler

This will run the filters on the abandoned wells asset
and select 1000 polygons to be processed with the
LEAF toolbox sampler.

Also, it will match the abandoned wells with their 
respective reference buffers which also will be
processed with the LEAF toolbox sampler.

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


import ee
from utils.utils import initialize_gee, get_feature_collection

