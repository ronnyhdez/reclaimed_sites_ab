"""
Flagging assets script.

This script will reads assets in GEE to create buffers around the
features and flags if the abandoned well polygon intersects one 
of those buffers. No filtering is done within this script. Flags
can be used by the final user to apply their own filters.

Also, the script creates a new property which contains the number 
of Landsat pixels that fit inside the abandoned well polygon, as
well a property indicating the earliest fire after the reclamation
date.

Given the API memory limits, each step creates an asset, which
is read in the next steps to create a new asset, and so on.

Author: Ronny A. Hernández Mora
"""

import os
import sys

module_path = os.path.abspath(os.path.join('..'))
if module_path not in sys.path:
    sys.path.append(module_path)
print(module_path)


import ee
import json
from utils.utils import (
    initialize_gee, buffer_feature, 
    apply_inward_dilation, check_empty_coordinates,
    get_feature_collection, export_if_not_exists,
    print_sample_info, create_reference_buffer
)

initialize_gee()

# First Asset | ABMI reservoirs + AER waterbodies ==========================================
abandoned_wells = get_feature_collection("projects/ee-ronnyale/assets/selected_polygons")
reservoirs = get_feature_collection("projects/ee-ronnyale/assets/reservoirs")
buffered_reservoirs = reservoirs.map(buffer_feature)
asset_image = ee.Image("projects/ee-eoagsaer/assets/LULC_2022_EE")

## Mask for waterbodies
water_mask = asset_image.eq(1)
water_image = asset_image.updateMask(water_mask)
## Reduce to vector to obtain polygons from raster
water_bodies_vector = water_image.reduceToVectors(
    geometryType="polygon",
    scale=10,  # LCC layer documentation states is 10m
    maxPixels=1e8,
    bestEffort=True,
    labelProperty="water_bodies",
)

buffered_waterbodies = water_bodies_vector.map(buffer_feature)

# Function to check if a well intersects with waterbodies or buffered waterbodies
def define_intersection(well):
    """
    Define polygons intersections with waterbodies or their buffers.
    TODO: Annotate origin of waterbodies data        
    """
    intersects_reservoirs = reservoirs.filterBounds(well.geometry()).size().gt(0)
    intersects_reservoirs_buffer = (
        buffered_reservoirs.filterBounds(well.geometry()).size().gt(0)
    )
    intersects_waterbodies = (
        water_bodies_vector.filterBounds(well.geometry()).size().gt(0)
    )
    intersects_waterbodies_buffer = (
        buffered_waterbodies.filterBounds(well.geometry()).size().gt(0)
    )
    return (
        well.set("intersects_waterbodies", intersects_waterbodies)
        .set("intersects_waterbody_buffer", intersects_waterbodies_buffer)
        .set("intersects_reservoirs", intersects_reservoirs)
        .set("intersects_reservoirs_buffer", intersects_reservoirs_buffer)
    )

wells_with_intersections = abandoned_wells.map(define_intersection)

export_if_not_exists('projects/ee-ronnyale/assets/intersecting_wells_flags',
                      wells_with_intersections,
                      'export_intersecting_wells_flags')

# Second Asset | ABMI Industrial + Residential + Roads ==========================================
abandoned_wells = get_feature_collection("projects/ee-ronnyale/assets/intersecting_wells_flags")
asset_industrial = get_feature_collection("projects/ee-ronnyale/assets/industrial")
asset_residential = get_feature_collection("projects/ee-ronnyale/assets/residentials")
asset_roads = get_feature_collection("projects/ee-ronnyale/assets/roads")
buffered_industrial = asset_industrial.map(buffer_feature)
buffered_residential = asset_residential.map(buffer_feature)
buffered_roads = asset_roads.map(buffer_feature)

def define_intersection(well):
    """
    Define polygons intersections with industrial/residential or roads areas or their
    buffers.
    """
    intersects_industrial = asset_industrial.filterBounds(well.geometry()).size().gt(0)
    intersects_industrial_buffer = (
        buffered_industrial.filterBounds(well.geometry()).size().gt(0)
    )
    intersects_residential = (
        asset_residential.filterBounds(well.geometry()).size().gt(0)
    )
    intersects_residential_buffer = (
        buffered_residential.filterBounds(well.geometry()).size().gt(0)
    )
    intersects_roads = asset_roads.filterBounds(well.geometry()).size().gt(0)
    intersects_roads_buffer = buffered_roads.filterBounds(well.geometry()).size().gt(0)
    return (
        well.set("intersects_industrial", intersects_industrial)
        .set("intersects_industrial_buffer", intersects_industrial_buffer)
        .set("intersects_residential", intersects_residential)
        .set("intersects_residential_buffer", intersects_residential_buffer)
        .set("intersects_roads", intersects_roads)
        .set("intersects_roads_buffer", intersects_roads_buffer)
    )

wells_with_intersections = abandoned_wells.map(define_intersection)

export_if_not_exists('projects/ee-ronnyale/assets/intersecting_wells_flags_v2',
                      wells_with_intersections,
                      'export_intersecting_wells_flags_v2')

# Third Asset | Disturbed polygons ==========================================
abandoned_wells = get_feature_collection(
    'projects/ee-ronnyale/assets/intersecting_wells_flags_v2')
fires = get_feature_collection('projects/ee-ronnyale/assets/fires')

def set_fire_year(well):
    """
    Set the fire year for each abandoned well
    """
    well_year = ee.Number(well.get('mx_bnd_'))
    well_geom = well.geometry()

    # Get fires intersecting with the well
    intersecting_fires = fires.filterBounds(well_geom)

    # Count the number of intersecting fire polygons
    intersecting_count = intersecting_fires.size()

    # If there are intersecting fires
    fire_year = ee.Algorithms.If(intersecting_count.gt(0),
                                 # More than one intersecting fire polygon
                                 ee.Algorithms.If(intersecting_count.gt(1),
                                 # Get the fire year that is closest and after the well year
                                                  ee.Algorithms.If(
                                     intersecting_fires.filter(ee.Filter.gte(
                                         'year', well_year)).size().gt(0),
                                     intersecting_fires.filter(
                                         ee.Filter.gte('year', well_year))
                                     .sort('year')
                                     .first()
                                     .get('year'),
                                     intersecting_fires.sort(
                                         'year', False).first().get('year')
                                 ),
        # If there is exactly one intersecting fire polygon, get its year
        intersecting_fires.first().get('year')
    ),
        # If there are no intersecting fire polygons, set the year to 9999
        9999
    )
    # Return properties
    return well.set('fire_year', fire_year) \
               .set('intersecting_fires', intersecting_count)

disturbed_wells = abandoned_wells.map(set_fire_year)

export_if_not_exists('projects/ee-ronnyale/assets/fire_disturbance_flags_v3',
                      disturbed_wells,
                      'fire_disturbance_flags_v3')

# Fourth Asset | Pixels within polygons ==========================================

# This steps will create an asset with less than the original observations
# Because the negative buffer returns some small abandoned_wells polygons
# without coordinates. Nonetheless, this asset works to join the pixel
# count to the entire flagged asset.

# First, we need the negative buffers to avoid edges: ==== 
feature_collection = get_feature_collection(
    "projects/ee-ronnyale/assets/fire_disturbance_flags_v3")

# Apply the function to each feature in the collection
dilated_abandoned_wells = feature_collection.map(apply_inward_dilation)

# There is no need to export results. Next step can be run withou memory problems

# Second, we need the # of pixels within those reduced polygons ====
pixels = (
    ee.Image.constant(1)
    .clip(dilated_abandoned_wells)
    .rename("pixels")
    .reproject(
        crs="EPSG:32512",  # UTM zone 12N
        scale=30,
    )
)

pixel_count = pixels.reduceRegions(
    collection=dilated_abandoned_wells, reducer=ee.Reducer.count(), scale=30
)

# Function to flag empty geometries (based on the coordinates of the geometry)
pixel_count_geom_flag = pixel_count.map(check_empty_coordinates)

# Filter out empty geometries (otherwise GEE will have an error exporting asset)
pixel_count_complete = pixel_count_geom_flag.filter(
    ee.Filter.eq('empty_buffer', 0))

export_if_not_exists('projects/ee-ronnyale/assets/pixel_count_negative_buffer_v4',
                      pixel_count_complete,
                      'export_pixel_count_negative_buffer_v4')

# Fifth Asset | Pixel count in original geometries asset ==========================================
pixel_count = get_feature_collection("projects/ee-ronnyale/assets/pixel_count_negative_buffer_v4")
abandoned_wells = get_feature_collection("projects/ee-ronnyale/assets/fire_disturbance_flags_v3")

# Define properties keys to perform the join
pixel_count_selected = pixel_count.select('count', 'wllst__')
join_filter = ee.Filter.equals(leftField = 'wllst__',
                               rightField = 'wllst__')
# Define the join
inner_join = ee.Join.saveAll(matchesKey = 'matches',
                             outer = True)
# Apply the join
joined = inner_join.apply(primary = abandoned_wells, 
                          secondary = pixel_count_selected, 
                          condition = join_filter)
# print_sample_info(joined)

# Function to merge properties and handle missing matches
def merge_properties(feature):
    matches = ee.List(feature.get('matches'))
    count = ee.Algorithms.If(matches.size().eq(0), 0, ee.Feature(matches.get(0)).get('count'))
    return feature.set('count', count).set('matches', None) 

merged = joined.map(merge_properties)
print_sample_info(merged)

export_if_not_exists('projects/ee-ronnyale/assets/pixel_count_flags_v5',
                      merged,
                      'export_pixel_count_flags_v5')

# Sixth Asset | Reference buffers ==========================================
polygons = get_feature_collection('projects/ee-ronnyale/assets/pixel_count_flags_v5')

buffer_only_polygons = polygons.map(create_reference_buffer)

export_if_not_exists('projects/ee-ronnyale/assets/reference_buffers',
                     buffer_only_polygons,
                     'export_reference_buffers')

# Seventh Asset | Reference buffers land cover area ==========================
image = ee.Image('projects/ee-ronnyale/assets/aer_lulc')

# Define original classes and the simplified version
original_classes = [0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13]
simplified_values = [
    0,  # 0 - Unclassified -> Unclassified
    2,  # 1 - Water -> Other
    4,  # 2 - Bryoids -> Other
    2,  # 3 - Wetland – Treed -> Wetland/Marsh/Swamp
    3,  # 4 - Herbs -> Crop/Herbaceous
    4,  # 5 - Exposed/Barren Land -> Other
    4,  # 6 - Shrubland -> Other
    2,  # 7 - Wetland -> Wetland/Marsh/Swamp
    3,  # 8 - Grassland -> Crop/Herbaceous
    1,  # 9 - Coniferous -> Forest
    1,  # 10 - Broadleaf -> Forest
    1,  # 11 - Mixedwood -> Forest
    3,  # 12 - Agriculture -> Crop/Herbaceous
    4,  # 13 - Developed -> Other
]

# Reclassify the image
reclassified_image = image.remap(original_classes, simplified_values)

# TODO: Probably export the reclassified image

# Function to calculate the area of each land cover class within the polygon
def calculate_class_area(feature):
    areas = ee.Image.pixelArea().addBands(reclassified_image) \
        .reduceRegion(
            reducer = ee.Reducer.sum().group(
                groupField = 1,
                groupName = 'class'
            ),
            geometry = feature.geometry(),
            scale = 10,
            maxPixels = 1e13
        )
    # Extract grouped dictionary
    grouped = ee.List(areas.get('groups'))

    # Conver list to dictionary
    areas_dict = ee.Dictionary(
        grouped.map(lambda item: ee.List([
            ee.String(ee.Dictionary(item).get('class')),
            ee.Number(ee.Dictionary(item).get('sum'))
        ])).flatten()
    )

    # Set the areas as properties of the feature
    return feature.set(areas_dict)

# Read the reference buffers asset and calculate land cover areas
reference = ee.FeatureCollection('projects/ee-ronnyale/assets/reference_buffers')
reference_areas = reference.map(calculate_class_area)

export_if_not_exists('projects/ee-ronnyale/assets/reference_buffers_lc_areas',
                     reference_areas,                    
                     'export_reference_land_cover_buffers')

# Eighth Asset | Reclaimed polygons land cover area ==========================
raw_reclaimed_sites = ee.FeatureCollection('projects/ee-ronnyale/assets/pixel_count_flags_v5');

reclaimed_sites_areas = raw_reclaimed_sites.map(calculate_class_area)

export_if_not_exists('projects/ee-ronnyale/assets/reclaimed_sites_areas_v6',
                     reclaimed_sites_areas,                    
                     'export_reclaimed_sites_areas')

