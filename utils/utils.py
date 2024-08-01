import ee
import sys

# Constants
BUFFER_SIZE = 30

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

def buffer_feature(feature, distance=BUFFER_SIZE):
    """Create buffers around features"""
    return feature.buffer(distance)

def assets_exists(asset_id):
    """Validate if asset exists in GEE"""
    try:
        ee.data.getAsset(asset_id)
        return True
    except Exception:
        return False

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
        print(f'No export for {asset_id}. Already exists')