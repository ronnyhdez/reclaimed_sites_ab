# Imports
import geopandas as gpd
import os
import sys
import janitor
import ee
import json

# Read data
sys.path.append(os.path.abspath(os.path.join('..')))
reservoirs = gpd.read_file('data_check/HFI2021.gdb',
                                # driver = 'FileGDB',
                                layer = 'o01_Reservoirs_HFI_2021')

reservoirs = reservoirs.clean_names()
reservoirs = reservoirs[['feature_ty', 'geometry']]
reservoirs = reservoirs[:10]
print(reservoirs.head())
print(f'Total number of reservoirs: {len(reservoirs)}')


ee.Initialize()

reservoirs_geojson = reservoirs.to_json()

# Load GeoJSON as an Earth Engine FeatureCollection
reservoirs_fc = ee.FeatureCollection(json.loads(reservoirs_geojson))
exportTask = ee.batch.Export.table.toAsset(
    collection=reservoirs_fc,
    description='Reservoirs Export',
    assetId='projects/ee-ronnyale/assets/reservoirs_test_v1'
)

# Start the export task
exportTask.start()
# # Fires shp for GEE
# fires = gpd.read_file('data/NFDB_poly/NFDB_poly_20210707.shp')
# fires = clean_names(fires)
# fires = fires[fires['src_agency'] == "AB"]

# # Drop elevation (Z and M values)
# fires_2d = fires.copy()
# fires_2d['geometry'] = fires_2d['geometry'].apply(lambda geom: geom if geom.is_empty else geom.dropna())


# import geemap
# import ee
# ee.Initialize()
# ee_object = geemap.geojson_to_ee('selected_polygons.geojson')

# exportTask = ee.batch.Export.table.toAsset(
#     collection = reservoirs,
#     description = 'description',
#     assetId = 'users/ronnyale/reclamation_ab'
# )
# exportTask.start()