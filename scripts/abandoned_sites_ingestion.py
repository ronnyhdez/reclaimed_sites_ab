
# Imports
import fiona
import geopandas as gpd
import os
import sys

# Read data
sys.path.append(os.path.abspath(os.path.join('..')))
abandoned_wells = gpd.read_file('data/HFI2021.gdb/HFI2021.gdb',
                                driver = 'FileGDB',
                                layer = 'o16_WellsAbnd_HFI_2021')

print(abandoned_wells.head())
