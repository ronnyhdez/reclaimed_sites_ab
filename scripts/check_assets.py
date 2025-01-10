import ee

# Initialize the Earth Engine API
ee.Initialize()

# def list_gee_assets(asset_path='users/ronnyale'):
#     """Lists all assets under a specified GEE asset path."""
#     assets = ee.data.listAssets({'parent': asset_path}).get('assets', [])
#     for asset in assets:
#         print(f"ID: {asset['id']} | Type: {asset['type']}")
# 
# # Replace 'users/ronnyale' with your GEE username or specific asset folder
# list_gee_assets('projects/ee-ronnyale/assets')

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

dest_folder = 'projects/ee-ronnyale/assets/fires_layer'
try:
    ee.data.createFolder(dest_folder)
except ee.ee_exception.EEException:
    print("Folder already exists")

# List all assets in your directory
source_folder = 'projects/ee-ronnyale/assets'
assets = ee.data.listAssets({'parent': source_folder})

# Move files that match the pattern
for asset in assets['assets']:
    asset_name = asset['name']
    if 'fires_batch_' in asset_name:
        try:
            # Get just the filename without the path
            filename = asset_name.split('/')[-1]
            # Create the new path
            new_path = f"{dest_folder}/{filename}"
            # Move the asset
            ee.data.renameAsset(asset_name, new_path)
            print(f"Moved {filename} to {dest_folder}")
        except ee.ee_exception.EEException as e:
            print(f"Error moving {filename}: {str(e)}")
