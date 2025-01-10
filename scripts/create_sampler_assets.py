"""
Create the assets to be used in the LEAFtoolbox sampler

This will run the filters on the abandoned wells asset
and select 1000 polygons to be processed with the
LEAF toolbox sampler.

Also, it will match the abandoned wells with their 
respective reference buffers which also will be
processed with the LEAF toolbox sampler.

Outputs:
- Two assets in GEE. One for the filtered abandoned wells and
  a second one for their reference buffers.

Usage:
- Run the script with the lates reclaimed sites version and
  reference buffers.
- The script will create all the filters, randomly select
  1000 abandoned wells polygons and their reference buffers 

Author: Ronny A. Hernández Mora
"""

import ee
import os
import sys

print("Current working directory:", os.getcwd())
parent_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
print("Parent directory: ", parent_dir)
sys.path.append(parent_dir)

from gee_helpers.gee_helpers import(
    initialize_gee, get_feature_collection,
    set_dates, set_area, export_if_not_exists
)

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

# Include properly dates for the sampler and add area:
non_intersecting_features = non_intersecting_features.map(set_dates)
non_intersecting_with_area = non_intersecting_features.map(set_area)

# Select a random sample
random_sample = non_intersecting_with_area.randomColumn().limit(1000, 'random')

# Reference buffers processing
reclaimed_ids = random_sample.aggregate_array('wllst__')

filtered_buffers = reference_buffers.filter(
    ee.Filter.inList('wllst__', reclaimed_ids))

# Format dates

# TODO:ref 207
# The code to format the dates could be somehwere aroung here.
# Given that this is a random selection, as today (20250109)
# i don't want to create a new random dataset which will have
# to be re-processed by the sampler

# Export both feature collections as assets to GEE
export_if_not_exists('projects/ee-ronnyale/assets/random_sample_1000_filtered_abandoned_wells',
                     random_sample,
                     'Export non-intersecting features')

export_if_not_exists('projects/ee-ronnyale/assets/random_sample_1000_filtered_reference_buffers',
                     filtered_buffers,
                     'Export selected abandoned wells buffers')
