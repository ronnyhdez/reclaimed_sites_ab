

import ee
import geemap
import json

ee.Initialize()

## Define function for buffers
def buffer_feature(feature):
    return feature.buffer(30)

# First Asset | ABMI reservoirs + AER waterbodies ==========================================

## Abandoned wells
asset_id = "projects/ee-ronnyale/assets/selected_polygons"
abandoned_wells = ee.FeatureCollection(asset_id)

## Reservoirs (already vector)
asset_id = "projects/ee-ronnyale/assets/reservoirs"
reservoirs = ee.FeatureCollection(asset_id)
buffered_reservoirs = reservoirs.map(buffer_feature)

## LULC asset
asset_id = "projects/ee-eoagsaer/assets/LULC_2022_EE"
asset_image = ee.Image(asset_id)

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

# Show a sample
sample = wells_with_intersections.limit(6).getInfo()
# sample = merged_results.limit(6).getInfo()
print(json.dumps(sample, indent=2))

# # Export the result with waterbodies and reservoirs
# export_asset_id = 'projects/ee-ronnyale/assets/intersecting_wells_flags'
# export_task = ee.batch.Export.table.toAsset(
#     collection=wells_with_intersections,
#     description='export_intersecting_wells_flags',
#     assetId=export_asset_id
# )
# export_task.start()


# Second Asset | ABMI Industrial + Residential + Roads ==========================================


## This would be the next step after the other asset import
asset_flagged = "projects/ee-ronnyale/assets/intersecting_wells_flags"
abandoned_wells = ee.FeatureCollection(asset_flagged)

## Industrial ABMI
asset_id = "projects/ee-ronnyale/assets/industrial"
asset_industrial = ee.FeatureCollection(asset_id)

## Residential ABMI
asset_id = "projects/ee-ronnyale/assets/residentials"
asset_residential = ee.FeatureCollection(asset_id)

## Roads ABMI
asset_id = "projects/ee-ronnyale/assets/roads"
asset_roads = ee.FeatureCollection(asset_id)

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

## Apply the intersection check to each well
test = wells_with_intersections.map(define_intersection)

## Show a sample
sample = test.limit(6).getInfo()
## sample = merged_results.limit(6).getInfo()
print(json.dumps(sample, indent=2))

# # Export the result with roads+residential+industrial
# export_asset_id = 'projects/ee-ronnyale/assets/intersecting_wells_flags_v2'
# export_task = ee.batch.Export.table.toAsset(
#     collection=wells_with_intersections,
#     description='export_intersecting_wells_flags_v2',
#     assetId=export_asset_id
# )
# export_task.start()

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


# Export the result with roads+residential+industrial
export_asset_id = 'projects/ee-ronnyale/assets/fire_disturbance_flags_v3'
export_task = ee.batch.Export.table.toAsset(
    collection=disturbed_wells,
    description='fire_disturbance_flags_v3',
    assetId=export_asset_id
)
export_task.start()

# Fourth Asset | Pixels within polygons ==========================================

# This steps will create an asset with less than the original observations
# Because the negative buffer returns some small abandoned_wells polygons
# without coordinates. Nonetheless, this asset works to join the pixel
# count to the entire flagged asset.

# First, we need the negative buffers to avoid edges: ==== 
asset = "projects/ee-ronnyale/assets/fire_disturbance_flags_v3"

feature_collection = ee.FeatureCollection(asset)

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


# Export the result with roads+residential+industrial
export_asset_id = 'projects/ee-ronnyale/assets/pixel_count_negative_buffer_v4'
export_task = ee.batch.Export.table.toAsset(
    collection=pixel_count_complete,
    description='export_pixel_count_negative_buffer_v4',
    assetId=export_asset_id
)
export_task.start()


# Fifth Asset | Pixel count in original geometries asset ==========================================
# ATTENTION: This one have to be v4 with pixel count
pixel_count = ee.FeatureCollection("projects/ee-ronnyale/assets/pixel_count_negative_buffer_v4")

# ATTENTION: This one have to be v3
abandoned_wells = ee.FeatureCollection("projects/ee-ronnyale/assets/fire_disturbance_flags_v3")

pixel_count_selected = pixel_count.select('count', 'wllst__')
primaryKey = 'wllst__'
secondaryKey = 'wllst__'

# Define a filter that matches features based on the keys
join_filter = ee.Filter.equals(leftField=primaryKey, rightField=secondaryKey)

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


export_asset_id = 'projects/ee-ronnyale/assets/pixel_count_flags_v5'
export_task = ee.batch.Export.table.toAsset(
    collection=merged,
    description='export_pixel_count_flags_v5',
    assetId=export_asset_id
)
export_task.start()
