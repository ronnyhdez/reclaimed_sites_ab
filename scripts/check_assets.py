import ee

# Initialize the Earth Engine API
ee.Initialize()

def list_gee_assets(asset_path='users/ronnyale'):
    """Lists all assets under a specified GEE asset path."""
    assets = ee.data.listAssets({'parent': asset_path}).get('assets', [])
    for asset in assets:
        print(f"ID: {asset['id']} | Type: {asset['type']}")

# Replace 'users/ronnyale' with your GEE username or specific asset folder
list_gee_assets('projects/ee-ronnyale/assets')

# deleted_assets = []
# for i in range(0, 700, 20):
#     asset_path = f'projects/ee-ronnyale/assets/_temp_batch_S2_{i}'
#     print(f'Deleting asset: {asset_path}')
#     try:
#         ee.data.deleteAsset(asset_path)
#         deleted_assets.append(asset_path)
#     except Exception as e:
#         print(f'Failed to delete {e}')
# 
# print(deleted_assets)
# 
# for i in range(1, 20):
#     asset_path = f'projects/ee-ronnyale/assets/reservoirs_batch_{i}'
#     print(f'We are deleting the asset: {asset_path}')
#     try:
#         ee.data.deleteAsset(asset_path)
#     except Exception as e:
#         print(f'Failed to delete {e}')
