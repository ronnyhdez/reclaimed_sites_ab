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

import ee
import json
import sys

try:
    ee.Initialize(opt_url='https://earthengine-highvolume.googleapis.com')
    print('Google Earth Engine has initialized successfully!')
except ee.EEException as e:
    print('Failed to initialize GEE', e)
except:
    print("Unexpected error:", sys.exc_info()[0])
    raise

## Define functions
def buffer_feature(feature):
    return feature.buffer(30)

def assets_exists(export_asset_id):
    try:
        ee.data.getAsset(export_asset_id)
        return True
    except:
        return False

def export_if_not_exists(asset_id, collection, description):
    if not assets_exists(asset_id):
        export_task = ee.batch.Export.table.toAsset(
            collection = collection,
            description = description,
            assetId = asset_id
        )
        export_task.start()
        print(f'Export task for {asset_id} started')
    else:
        print(f'No export for {asset_id}. Already exists')


# First Asset | ABMI reservoirs + AER waterbodies ==========================================

## Abandoned wells
abandoned_wells = ee.FeatureCollection("projects/ee-ronnyale/assets/selected_polygons")

## Reservoirs (already vector)
reservoirs = ee.FeatureCollection("projects/ee-ronnyale/assets/reservoirs")
buffered_reservoirs = reservoirs.map(buffer_feature)

## LULC asset
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

## Create buffer of waterbodies
buffered_waterbodies = water_bodies_vector.map(buffer_feature)

# Function to check if a well intersects with waterbodies or buffered waterbodies
def define_intersection(well):
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

# Apply the intersection check to each well
wells_with_intersections = abandoned_wells.map(define_intersection)

export_if_not_exists('projects/ee-ronnyale/assets/intersecting_wells_flags',
                      wells_with_intersections,
                      'export_intersecting_wells_flags')

# Second Asset | ABMI Industrial + Residential + Roads ==========================================

## This would be the next step after the other asset import
abandoned_wells = ee.FeatureCollection("projects/ee-ronnyale/assets/intersecting_wells_flags")

## Industrial ABMI
asset_industrial = ee.FeatureCollection("projects/ee-ronnyale/assets/industrial")

## Residential ABMI
asset_residential = ee.FeatureCollection("projects/ee-ronnyale/assets/residentials")

## Roads ABMI
asset_roads = ee.FeatureCollection("projects/ee-ronnyale/assets/roads")

## Create buffer industrial-residential-roads
buffered_industrial = asset_industrial.map(buffer_feature)
buffered_residential = asset_residential.map(buffer_feature)
buffered_roads = asset_roads.map(buffer_feature)

## Function to add values
def define_intersection(well):
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

## Apply the intersection check to each well
wells_with_intersections = abandoned_wells.map(define_intersection)

export_if_not_exists('projects/ee-ronnyale/assets/intersecting_wells_flags_v2',
                      wells_with_intersections,
                      'export_intersecting_wells_flags_v2')

# XXXX Asset | AER wetland_treed + wetland ==========================================

#########################################
### NOT USED ON FLAGGING OR FILTERING ###
#########################################

# # Abandoned wells
# asset_id = 'projects/ee-ronnyale/assets/selected_polygons'
# abandoned_wells = ee.FeatureCollection(asset_id)

# # LULC asset
# asset_id = 'projects/ee-eoagsaer/assets/LULC_2022_EE'
# asset_image = ee.Image(asset_id)

# # # This would be the next step after the other asset import
# # asset_flagged = 'projects/ee-ronnyale/assets/intersecting_wells_flags'
# # abandoned_wells = ee.FeatureCollection(asset_flagged)

# # Mask for wetland-treed
# wetland_treed_mask = asset_image.eq(3)
# wetland_treed_image = asset_image.updateMask(wetland_treed_mask)
# # Reduce to vector
# wetland_treed_vector = wetland_treed_image.reduceToVectors(
#     geometryType='polygon',
#     scale=10,
#     maxPixels=1e8,
#     bestEffort=True,
#     labelProperty='wetland_treed'
# )

# # Create buffer wetland treed
# buffered_wetland_treed = wetland_treed_vector.map(buffer_feature)

# # Mask for wetland
# wetland_mask = asset_image.eq(7)
# wetland_image = asset_image.updateMask(wetland_mask)
# # Reduce to vector
# wetland_vector = wetland_image.reduceToVectors(
#     geometryType='polygon',
#     scale=10,
#     maxPixels=1e8,
#     bestEffort=True,
#     labelProperty='wetland'
# )

# # Create buffer wetland
# buffered_wetland = wetland_vector.map(buffer_feature)

# # Function to add values
# def define_intersection(well):
#     intersects_wetland_treed = wetland_treed_vector.filterBounds(
#         well.geometry()).size().gt(0)
#     intersects_wetland_treed_buffer = buffered_wetland_treed.filterBounds(
#         well.geometry()).size().gt(0)
#     # intersects_wetland = wetland_vector.filterBounds(
#     #     well.geometry()).size().gt(0)
#     # intersects_wetland_buffer = buffered_wetland.filterBounds(
#     #     well.geometry()).size().gt(0)
#     return well.set('intersects_wetland_treed', intersects_wetland_treed) \
#                .set('intersects_wetland_treed_buffer', intersects_wetland_treed_buffer)  # \
#     #    .set('intersects_wetland', intersects_wetland) \
#     #    .set('intersects_wetland_buffer', intersects_wetland_buffer)


# # Apply the intersection check to each well
# wells_with_intersections = abandoned_wells.map(define_intersection)

# # Apply the intersection check to each well
# test = wells_with_intersections.map(define_intersection)

# # Show a sample
# sample = test.limit(6).getInfo()
# # sample = merged_results.limit(6).getInfo()
# print(json.dumps(sample, indent=2))

# Third Asset | Disturbed polygons ==========================================
abandoned_wells = ee.FeatureCollection(
    'projects/ee-ronnyale/assets/intersecting_wells_flags_v2')
fires = ee.FeatureCollection('projects/ee-ronnyale/assets/fires')

# Function to set the fire year for each abandoned well
def set_fire_year(well):
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

# Map the function over the abandoned wells collection
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
feature_collection = ee.FeatureCollection("projects/ee-ronnyale/assets/fire_disturbance_flags_v3")

# Function to apply inward buffer to each feature
def apply_inward_dilation(feature):
    buffered_feature = feature.buffer(-30, 1)
    return buffered_feature

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
def check_empty_coordinates(feature):
    coordinates = feature.geometry().coordinates()
    is_empty = coordinates.size().eq(0)
    return feature.set('empty_buffer', is_empty)

# Apply function
pixel_count_geom_flag = pixel_count.map(check_empty_coordinates)

# Filter out empty geometries (otherwise GEE will have an error exporting asset)
pixel_count_complete = pixel_count_geom_flag.filter(
    ee.Filter.eq('empty_buffer', 0))

export_if_not_exists('projects/ee-ronnyale/assets/pixel_count_negative_buffer_v4',
                      pixel_count_complete,
                      'export_pixel_count_negative_buffer_v4')

# Fifth Asset | Pixel count in original geometries asset ==========================================
pixel_count = ee.FeatureCollection("projects/ee-ronnyale/assets/pixel_count_negative_buffer_v4")
abandoned_wells = ee.FeatureCollection("projects/ee-ronnyale/assets/fire_disturbance_flags_v3")

# Define properties keys to perform the join
pixel_count_selected = pixel_count.select('count', 'wllst__')
join_filter = ee.Filter.equals(leftField='wllst__', rightField='wllst__')

# Define the join
inner_join = ee.Join.saveAll(matchesKey='matches', outer=True)

# Apply the join
joined = inner_join.apply(primary=abandoned_wells, secondary=pixel_count_selected, condition=join_filter)
# print(joined.limit(1).getInfo())
# result = joined.limit(2).getInfo()
# print(json.dumps(merged, indent = 2))

# Function to merge properties and handle missing matches
def merge_properties(feature):
    matches = ee.List(feature.get('matches'))
    count = ee.Algorithms.If(matches.size().eq(0), 0, ee.Feature(matches.get(0)).get('count'))
    return feature.set('count', count).set('matches', None) 

# Map the function over the joined FeatureCollection
merged = joined.map(merge_properties)
# print(merged.limit(1).getInfo())
# result = merged.limit(2).getInfo()
# print(json.dumps(merged, indent = 2))

export_if_not_exists('projects/ee-ronnyale/assets/pixel_count_flags_v5',
                      merged,
                      'export_pixel_count_flags_v5')

# Sixth Asset | Reference buffers ==========================================
polygons = ee.FeatureCollection('projects/ee-ronnyale/assets/pixel_count_flags_v5')

def create_well_buffer(feature):
    buffer_geometry = feature.buffer(30, 1)
    buffer_geometry_feature = buffer_geometry.geometry()
    reference_buffer = buffer_geometry_feature.buffer(90, 1)
    buffer_only_geometry = reference_buffer.difference(buffer_geometry_feature)
    wllst_value = feature.get('wllst__')
    buffer_feature = ee.Feature(buffer_only_geometry).set('wllst__', wllst_value)    
    return buffer_feature

# Apply the buffer function to the polygons feature collection
buffer_only_polygons = polygons.map(create_well_buffer)

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
reference = ee.FeatureCollection('projects/ee-ronnyale/assets/reference_buffers_test_gee')
reference_areas = reference.map(calculate_class_area)

export_if_not_exists('projects/ee-ronnyale/assets/reference_buffers_lc_areas',
                     reference_areas,                    
                     'export_reference_land_cover_buffers')

