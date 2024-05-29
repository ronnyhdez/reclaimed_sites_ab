

import ee
import geemap
import json

ee.Initialize()

## Define function for buffers
def buffer_feature(feature):
    return feature.buffer(30)

# First Asset | ABMI reservoirs + AER waterbodies ----

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

# # Show a sample
# sample = wells_with_intersections.limit(6).getInfo()
# # sample = merged_results.limit(6).getInfo()
# print(json.dumps(sample, indent=2))

# # Export the result with waterbodies and reservoirs
# export_asset_id = 'projects/ee-ronnyale/assets/intersecting_wells_flags'
# export_task = ee.batch.Export.table.toAsset(
#     collection=wells_with_intersections,
#     description='export_intersecting_wells_flags',
#     assetId=export_asset_id
# )
# export_task.start()


# Second Asset | ABMI Industrial + Residential + Roads ----


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

# Third Asset | AER wetland_treed + wetland ----

# Abandoned wells
asset_id = 'projects/ee-ronnyale/assets/selected_polygons'
abandoned_wells = ee.FeatureCollection(asset_id)

# LULC asset
asset_id = 'projects/ee-eoagsaer/assets/LULC_2022_EE'
asset_image = ee.Image(asset_id)

# # This would be the next step after the other asset import
# asset_flagged = 'projects/ee-ronnyale/assets/intersecting_wells_flags'
# abandoned_wells = ee.FeatureCollection(asset_flagged)

# Mask for wetland-treed
wetland_treed_mask = asset_image.eq(3)
wetland_treed_image = asset_image.updateMask(wetland_treed_mask)
# Reduce to vector
wetland_treed_vector = wetland_treed_image.reduceToVectors(
    geometryType='polygon',
    scale=10,
    maxPixels=1e8,
    bestEffort=True,
    labelProperty='wetland_treed'
)

# Create buffer wetland treed
buffered_wetland_treed = wetland_treed_vector.map(buffer_feature)

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

# Function to add values


def define_intersection(well):
    intersects_wetland_treed = wetland_treed_vector.filterBounds(
        well.geometry()).size().gt(0)
    intersects_wetland_treed_buffer = buffered_wetland_treed.filterBounds(
        well.geometry()).size().gt(0)
    # intersects_wetland = wetland_vector.filterBounds(
    #     well.geometry()).size().gt(0)
    # intersects_wetland_buffer = buffered_wetland.filterBounds(
    #     well.geometry()).size().gt(0)
    return well.set('intersects_wetland_treed', intersects_wetland_treed) \
               .set('intersects_wetland_treed_buffer', intersects_wetland_treed_buffer)  # \
    #    .set('intersects_wetland', intersects_wetland) \
    #    .set('intersects_wetland_buffer', intersects_wetland_buffer)


# Apply the intersection check to each well
wells_with_intersections = abandoned_wells.map(define_intersection)

# Apply the intersection check to each well
test = wells_with_intersections.map(define_intersection)

# Show a sample
sample = test.limit(6).getInfo()
# sample = merged_results.limit(6).getInfo()
print(json.dumps(sample, indent=2))