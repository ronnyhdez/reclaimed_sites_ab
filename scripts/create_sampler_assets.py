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
from utils.utils import initialize_gee, get_feature_collection, set_dates

# Start the process
initialize_gee()

abandoned_wells = get_feature_collection(
    "projects/ee-ronnyale/assets/reclaimed_sites_areas_v6")
reference_buffers = get_feature_collection(
    'projects/ee-ronnyale/assets/reference_buffers_lc_areas')

# Abandoned wells processing
filters = [
    # Get all polygons without an intersetion
    ee.Filter.eq("intersects_industrial", 0),
    ee.Filter.eq("intersects_industrial_buffer", 0),
    ee.Filter.eq("intersects_reservoirs", 0),
    ee.Filter.eq("intersects_reservoirs_buffer", 0),
    ee.Filter.eq("intersects_residential", 0),
    ee.Filter.eq("intersects_residential_buffer", 0),
    ee.Filter.eq("intersects_roads", 0),
    ee.Filter.eq("intersects_roads_buffer", 0),
    ee.Filter.eq("intersects_waterbodies", 0),
    ee.Filter.eq("intersects_waterbody_buffer", 0),
    # Get polygons with more or equal to 1 landsat pixel
    ee.Filter.greaterThan("count", 0),
    # Get polygons without fire disturbance
    ee.Filter.eq("fire_year", 9999),
]

combined_filter = ee.Filter.And(*filters)
non_intersecting_features = abandoned_wells.filter(combined_filter)
# Include properly dates for the sampler:
non_intersecting_features = non_intersecting_features.map(set_dates)

# Reference buffers processing
reclaimed_ids = non_intersecting_features.aggregate_array('wllst__')
filtered_buffers = reference_buffers.filter(
    ee.Filter.inList('wllst__', reclaimed_ids))

task = ee.batch.Export.table.toAsset(
    collection = non_intersecting_features,
    description = 'Export non-intersecting features',
    assetId = "random_sample_1000_filtered_abandoned_wells"
)
task.start()