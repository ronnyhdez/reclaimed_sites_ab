"""
Create the selected abandoned wells asset

This will run filters according to the reclamation
status. Specifically, it will select just those
abandoned wells wich status is 'reclaimed'. Then
it will validate dates according to the variables
reclamation date, maximum abandoned date, and 
maximum last production date.

The abandoned wells that pass those filters will
be exported as an asset to GEE to be use for
flagging (intersecting features from the assets derived
from 'shp_exports_for_assets.R')

Outputs:
- 'selected_abandoned_wells' asset in GEE.

Usage:
- ...

Author: Ronny A. Hernández Mora
"""

# Imports
import fiona
import geopandas as gpd
import pandas as pd
import os
import sys
import janitor

# Read data
sys.path.append(os.path.abspath(os.path.join('..')))
abandoned_wells = gpd.read_file('data_check/HFI2021.gdb',
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

# Save to geojson
selected_polygons.to_file('data/selected_polygons.geojson', driver='GeoJSON') 
