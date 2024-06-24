
# Imports
import fiona
import geopandas as gpd
import pandas as pd
import os
import sys
import janitor
import ee

# Read data
sys.path.append(os.path.abspath(os.path.join('..')))

data_directory = os.path.join(sys.path[-1], 'data/HFI2021.gdb/HFI2021.gdb')

abandoned_wells = gpd.read_file(data_directory,
                                driver = 'FileGDB',
                                layer = 'o16_WellsAbnd_HFI_2021')

# print(abandoned_wells.head())

# Clean column names
abandoned_wells = abandoned_wells.clean_names()

len_abandoned_wells = len(abandoned_wells)
print("Number of observations after filtering: ", len_abandoned_wells) 

# Map reclamation values
abandoned_wells['reclamation_status'] = abandoned_wells['reclamation_status'].map({
    1: 'not_reclaimed',
    2: 'reclamation_exempt',
    3: 'reclaimed'
}).fillna('no_data')

# Filter polygons
selected_polygons = (
        abandoned_wells
        .query("reclamation_status == 'reclaimed'")
        .query("reclamation_date != 0")
        .query("reclamation_date > max_abandoned_date")
        .query("reclamation_date > max_last_production_date")
        .query("max_abandoned_date > max_last_production_date")
)

len_polygons = len(selected_polygons)
print("Number of observations after filtering: ", len_polygons) 

# # Save to geojson
# selected_polygons.to_file('data/selected_polygons.geojson', driver='GeoJSON') 

ee.Initialize()

export_asset_id = 'projects/ee-ronnyale/assets/intersecting_wells_flags_check_names'
export_task = ee.batch.Export.table.toAsset(
    collection=selected_polygons,
    description='export_intersecting_wells_flags_check_names',
    assetId=export_asset_id
)
export_task.start()