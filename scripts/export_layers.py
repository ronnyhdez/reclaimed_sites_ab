# Imports
import geopandas as gpd
import os
import sys
import janitor
import ee
import json
import math
import time

# # # Fires shp for GEE
# # fires = gpd.read_file('data/NFDB_poly/NFDB_poly_20210707.shp')
# # fires = clean_names(fires)
# # fires = fires[fires['src_agency'] == "AB"]

# # # Drop elevation (Z and M values)
# # fires_2d = fires.copy()
# # fires_2d['geometry'] = fires_2d['geometry'].apply(lambda geom: geom if geom.is_empty else geom.dropna())
import geopandas as gpd
import os
import sys
import ee
import json
import math
import time

def wait_for_tasks(task_list):
    while True:
        tasks_completed = all(task.status()['state'] in ['COMPLETED', 'FAILED', 'CANCELLED'] for task in task_list)
        if tasks_completed:
            break
        time.sleep(10)  

    # Check for any failed tasks
    failed_tasks = [task for task in task_list if task.status()['state'] == 'FAILED']
    if failed_tasks:
        raise Exception(f"The following tasks failed: {', '.join(task.status()['description'] for task in failed_tasks)}")

def process_layer(layer_name, data):
    print(f"Processing {layer_name}...")

    print(f'Total number of {layer_name}: {len(data)}')
    print(f'Original data CRS: {data.crs}')

    batch_size = 500

    # Calculate the number of batches needed
    num_batches = math.ceil(len(data) / batch_size)
    print(f'Total of batches to export: {num_batches}')

    export_tasks = []

    for i, batch in enumerate(data.groupby(data.index // batch_size)):
        # Reproject to WGS 84 (EPSG:4326)
        batch = batch[1].to_crs(epsg=4326)

        # Convert to GeoJSON
        batch_geojson = batch.to_json()

        # Load GeoJSON as an Earth Engine FeatureCollection
        print(f'Transforming to json batch {i}')
        batch_fc = ee.FeatureCollection(json.loads(batch_geojson))

        # Define a unique asset ID for each batch
        batch_asset_id = f'projects/ee-ronnyale/assets/{layer_name}_batch_{i+1}'

        # Export the batch to GEE
        print(f'Exporting the batch: {batch_asset_id}')
        exportTask = ee.batch.Export.table.toAsset(
            collection=batch_fc,
            description=f'{layer_name.capitalize()} Batch {i+1}',
            assetId=batch_asset_id
        )

        # Start the export task
        exportTask.start()
        export_tasks.append(exportTask)

    # Wait for all batch export tasks to complete
    print(f"Waiting for all {layer_name} batch export tasks to complete...")
    wait_for_tasks(export_tasks)
    print(f"All {layer_name} batch export tasks completed successfully.")

    batch_asset_ids = [f'projects/ee-ronnyale/assets/{layer_name}_batch_{i+1}' for i in range(num_batches)]
    merged_fc = ee.FeatureCollection(batch_asset_ids[0])

    for asset_id in batch_asset_ids[1:]:
        print(f'Merging batch {asset_id}')
        batch_fc = ee.FeatureCollection(asset_id)
        merged_fc = merged_fc.merge(batch_fc)

    print(f'Done merging {layer_name} batches...')
    print(f'Total number of features: {merged_fc.size().getInfo()}')

    # Export the merged collection to another asset
    exportTask = ee.batch.Export.table.toAsset(
        collection=merged_fc,
        description=f'Merged {layer_name.capitalize()}',
        assetId=f'projects/ee-ronnyale/assets/{layer_name}_merged'
    )
    print(f'Exporting merged {layer_name} asset')
    exportTask.start()

    # Wait for the merged asset export to complete
    print(f"Waiting for merged {layer_name} asset export to complete...")
    wait_for_tasks([exportTask])
    print(f"Merged {layer_name} asset export completed successfully.")

    print(f'Deleting individual {layer_name} batch assets...')
    for asset_id in batch_asset_ids:
        try:
            ee.data.deleteAsset(asset_id)
            print(f'Successfully deleted: {asset_id}')
        except Exception as e:
            print(f'Failed to delete {asset_id}: {e}')

    print(f"Finished processing {layer_name}.")

# Main execution
if __name__ == "__main__":
    ee.Initialize()

    # Read data
    sys.path.append(os.path.abspath(os.path.join('..')))
    reservoirs = gpd.read_file('data_check/HFI2021.gdb',
                                    layer = 'o01_Reservoirs_HFI_2021')
    reservoirs = reservoirs.clean_names()
    reservoirs = reservoirs[['feature_ty', 'geometry']]

    roads = gpd.read_file('data_check/HFI2021.gdb',
                                    layer = 'o03_Roads_HFI_2021')
    roads = roads.clean_names()
    roads = roads[['feature_ty', 'geometry']]

    residentials = gpd.read_file('data_check/HFI2021.gdb',
                                    layer = 'o15_Residentials_HFI_2021')
    residentials = residentials.clean_names()
    residentials = residentials[['feature_ty', 'geometry']]

    industrials = gpd.read_file('data_check/HFI2021.gdb',
                                    layer = 'o08_Industrials_HFI_2021')
    industrials = industrials.clean_names()
    industrials = industrials[['feature_ty', 'geometry']]

    # Define the layers to process
    layers = [
        ('reservoirs', reservoirs),
        ('residentials', residentials),
        ('roads', roads),
        ('industrials', industrials)
    ]

    # Process each layer
    for layer_name, layer_data in layers:
        process_layer(layer_name, layer_data)

    print("All layers have been processed successfully.")

# # Define the batch size
# batch_size = 500

# # Calculate the number of batches needed
# num_batches = math.ceil(len(reservoirs) / batch_size)
# print(f'Total of batches to export: {num_batches}')
# export_tasks = []

# for i, batch in enumerate(reservoirs.groupby(reservoirs.index // batch_size)):
#     # Reproject to WGS 84 (EPSG:4326)
#     batch = batch[1].to_crs(epsg=4326)

#     # Convert to GeoJSON
#     batch_geojson = batch.to_json()

#     # Load GeoJSON as an Earth Engine FeatureCollection
#     print(f'Transformin to json batch {i}')
#     batch_fc = ee.FeatureCollection(json.loads(batch_geojson))

#     # Define a unique asset ID for each batch
#     batch_asset_id = f'projects/ee-ronnyale/assets/reservoirs_batch_{i+1}'

#     # Export the batch to GEE
#     print(f'Exporting the batch: {batch_asset_id}')
#     exportTask = ee.batch.Export.table.toAsset(
#         collection = batch_fc,
#         description = f'Reservoirs Batch {i+1}',
#         assetId = batch_asset_id
#     )

#     # Start the export task
#     exportTask.start()
#     export_tasks.append(exportTask)

# # Wait for all batch export tasks to complete
# print("Waiting for all batch export tasks to complete in GEE...")
# wait_for_tasks(export_tasks)
# print("All batch export tasks completed successfully.")

# batch_asset_ids = [f'projects/ee-ronnyale/assets/reservoirs_batch_{i+1}' for i in range(num_batches)]
# reservoirs_fc = ee.FeatureCollection(batch_asset_ids[0])

# for asset_id in batch_asset_ids[1:]:
#     print(f'Merging batch {asset_id}')
#     batch_fc = ee.FeatureCollection(asset_id)
#     reservoirs_fc = reservoirs_fc.merge(batch_fc)

# print('Done merging batches...')
# print(f'Total number of features: {reservoirs_fc.size().getInfo()}')

# exportTask = ee.batch.Export.table.toAsset(
#     collection=reservoirs_fc,
#     description='Merged Reservoirs',
#     assetId='projects/ee-ronnyale/assets/reservoirs_merged'
# )
# print('Exporting merged asset')
# exportTask.start()

# # Wait for the merged asset export to complete
# print("Waiting for merged asset export to complete in GEE...")
# wait_for_tasks([exportTask])
# print("Merged asset export completed successfully.")


# print('Deleting individual batch assets...')
# for asset_id in batch_asset_ids:
#     try:
#         ee.data.deleteAsset(asset_id)
#         print(f'Successfully deleted: {asset_id}')
#     except Exception as e:
#         print(f'Failed to delete {asset_id}: {e}')







