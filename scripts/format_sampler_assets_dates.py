

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
    'projects/ee-ronnyale/assets/random_sample_1000_filtered_abandoned_wells')
reference_buffers = get_feature_collection(
    'projects/ee-ronnyale/assets/random_sample_1000_filtered_reference_buffers')

def rename_property(feature):
    # Convert year to integer and create timestamps
    year = ee.Number(feature.get('rclmtn_d')).int()
    time_start = ee.Date.fromYMD(year, 1, 1).millis()
    time_end = ee.Date.fromYMD(2023, 1, 1).millis()
    
    return feature \
        .set('system:time_start', time_start) \
        .set('system:time_end', time_end)

# Apply the date formatting to both collections
updated_wells = abandoned_wells.map(rename_property)
updated_buffers = reference_buffers.map(rename_property)

# Export both feature collections as assets to GEE
#export_if_not_exists('projects/ee-ronnyale/assets/random_sample_1000_filtered_abandoned_wells',
#                     random_sample,
#                     'Export non-intersecting features')
#
#export_if_not_exists('projects/ee-ronnyale/assets/random_sample_1000_filtered_reference_buffers',
#                     filtered_buffers,
#                     'Export selected abandoned wells buffers')
