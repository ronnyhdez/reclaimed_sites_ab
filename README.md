# reclaimed_sites_ab

You can use this EE code to generate 1985-2021 land change map:
https://code.earthengine.google.com/066804d8f05924247586393705c539b8 (red
disturbance and green vegetation regeneration)

NRCan land cover and land change data based on Landsat 1985-2020:
https://opendata.nfis.org/mapserver/nfis-change_eng.html

AAFC land cover data:
https://developers.google.com/earth-engine/datasets/catalog/AAFC_ACI#bands

The 2020 land cover classification of Alberta (Sentinel-2):
https://ags.aer.ca/publication/dig-2021-0019  (EE Asset 2022:
projects/ee-eoagsaer/assets/LULC_2022_EE, please see the AGS link for
description of classes; the metadata of the AGS DIG includes process steps and
accuracy assessments).

Abandoned well site data with reclamation status is publicly available for
download from the ABMI dataset; this one has the construction and reclamation
date too:
https://abmi.ca/home/data-analytics/da-top/da-product-overview/Human-Footprint-Products/HF-inventory.html
(use year 2021 and class 16 - abandoned wellsites)

Alberta Ground Cover Classification 2000:
https://open.alberta.ca/opendata/gda-f2fcfcfb-e3e6-4c00-a338-c90083c58b7e

EE fire data: https://developers.google.com/earth-engine/datasets/catalog/FIRMS
(https://developers.google.com/earth-engine/datasets/tags/fire)

National fire database: https://cwfis.cfs.nrcan.gc.ca/ha/nfdb

1. ABMI Wall-to-Wall Landcover 2000 and 2010 datasets (available for download
   here). These are quite dated, and are roughly based on an update of
   previously existing Landsat-based landcover mapping (e.g., EOSD).

2. In addition to the above, we have a much more recent Alberta Wetland
   Inventory dataset (based largely on Sentinel), which maps wetland classes
   across the province (available here).

3. ABMI's Human Footprint Inventory 2021 is our most recent human footprint
   dataset for Alberta (available here), which could be helpful for filtering
   areas by post-reclamation disturbance. 
