
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

# Get the assets
## In this case, the assets are the ones already created and to be consumed
## by the run_sampler.py script. I don't want to create an new set of
## observations because it's gonna take too long to re-run the entire
## process.
abandoned_wells = get_feature_collection(
    'projects/ee-ronnyale/assets/random_sample_1000_filtered_abandoned_wells')
reference_buffers = get_feature_collection(
    'projects/ee-ronnyale/assets/random_sample_1000_filtered_reference_buffers')

# Function to format date from the abandoned wells
## This is due to the LEAFtoolbox sampler code. If not formatted this way
## the sampler code will return an error.
def rename_property(feature):
    # Convert year to integer and create timestamps
    year = ee.Number(feature.get('rclmtn_d')).int()
    time_start = ee.Date.fromYMD(year, 1, 1).millis()
    time_end = ee.Date.fromYMD(2023, 1, 1).millis()
    
    return feature \
        .set('system:time_start', time_start) \
        .set('system:time_end', time_end)

# Apply the date formatting to the abandoned wells
## This is the asset that contains the date propertie 
updated_wells = abandoned_wells.map(rename_property)

# Copy the date to the reference buffers
## The buffers asset does not contains a date propertie. Given that they
## are buffers for each of the abandoned wells, we can just copy the date
## in order to process the buffers with the LEAF-toolbox.
def transfer_time_properties(feature):
    matches = ee.List(feature.get('matches'))
    well = ee.Feature(matches.get(0))
    
    # Get the time properties we just created in updated_wells
    time_start = well.get('system:time_start')
    time_end = well.get('system:time_end')
    
    return feature \
        .set('system:time_start', time_start) \
        .set('system:time_end', time_end) \
        .set('matches', None)

filter = ee.Filter.equals(
    leftField='wllst__',
    rightField='wllst__'
)

join = ee.Join.saveAll(
    matchesKey='matches',
    outer = True
)

joined = join.apply(
    primary=reference_buffers,
    secondary=abandoned_wells,
    condition=filter
)

updated_buffers = joined.map(transfer_time_properties)

# Export both feature collections as assets to GEE
#export_if_not_exists('projects/ee-ronnyale/assets/random_sample_1000_filtered_abandoned_wells_date_formatted',
#                     updated_wells,
#                     'Export non-intersecting features')

export_if_not_exists('projects/ee-ronnyale/assets/random_sample_1000_filtered_reference_buffers_date_formatted',
                     updated_buffers,
                     'Export selected abandoned wells buffers')
