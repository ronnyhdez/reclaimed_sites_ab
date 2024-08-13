import ee
import json
import sys

def initialize_gee():
    """Initialize GEE"""
    try:
        ee.Initialize(opt_url='https://earthengine-highvolume.googleapis.com')
        print('Google Earth Engine has initialized successfully!')
    except ee.EEException as e:
        print('Failed to initialize GEE', e)
    except:
        print("Unexpected error:", sys.exc_info()[0])
        raise

def buffer_feature(feature, distance=30):
    """Create buffers around features"""
    return feature.buffer(distance)

def apply_inward_dilation(feature, distance=-30):
    """Apply inward buffer to each feature."""
    return feature.buffer(distance, 1)

def create_reference_buffer(feature):
    """
    Define the "donut" buffers use to evaluate as
    a reference for the abandoned wells.    
    """
    buffer_geometry = feature.buffer(30, 1)
    buffer_geometry_feature = buffer_geometry.geometry()
    reference_buffer = buffer_geometry_feature.buffer(90, 1)
    buffer_only_geometry = reference_buffer.difference(buffer_geometry_feature)
    wllst_value = feature.get('wllst__')
    buffer_feature = ee.Feature(buffer_only_geometry).set('wllst__', wllst_value)    
    return buffer_feature

def assets_exists(asset_id):
    """Validate if asset exists in GEE"""
    try:
        ee.data.getAsset(asset_id)
        return True
    except Exception:
        return False

def get_feature_collection(asset_id):
    """Check if an asset exists and return it as a FeatureCollection if it does."""
    try:
        if assets_exists(asset_id):
            return ee.FeatureCollection(asset_id)
        else:
            raise ValueError(f"Asset {asset_id} does not exist.")
    except Exception as e:
        raise ValueError(f"Error loading asset {asset_id}: {str(e)}")

def export_if_not_exists(asset_id, collection, description):
    """Export an asset only if it doesn't exists in GEE"""
    if not assets_exists(asset_id):
        export_task = ee.batch.Export.table.toAsset(
            collection = collection,
            description = description,
            assetId = asset_id
        )
        export_task.start()
        print(f'Export task for {asset_id} started')
    else:
        print(f'Export skipped: Asset already exists at {asset_id}')

def check_empty_coordinates(feature):
    """Flag empty geometries based on the coordinates of the geometry."""
    coordinates = feature.geometry().coordinates()
    is_empty = coordinates.size().eq(0)
    return feature.set('empty_buffer', is_empty)

def print_sample_info(feature_collection, limit=2):
    """
    Print a sample of the feature collection information.
    
    Args:
        feature_collection (ee.FeatureCollection): The feature collection to sample.
        limit (int): The number of features to sample. Default is 2.
    """
    sample = feature_collection.limit(limit).getInfo()
    print(json.dumps(sample, indent=2))

def set_dates(feature):
    """
    Set date properly to be consumed and processed with the
    LEAFtoolbox sampler

    Args:
        feature: The feature collection to be processed
    """
    year = ee.Number(feature.get('rclmtn_d')).int()
    time_start = ee.Date.fromYMD(year, 1, 1).millis()
    time_end = ee.Date.fromYMD(2023, 1, 1).millis()
    # Set the 'system:time_start' and 'system:time_end' properties
    feature = feature.set('system:time_start', time_start) \
                     .set('system:time_end', time_end)
    
    return feature

def set_area(feature):
    """
    Set the area in a feature collection. To be used
    with a map in desired feature collection.

    Args:
        feature: The feature collection to be processed
    """
    area = feature.geometry().area()
    return feature.set('area', area)