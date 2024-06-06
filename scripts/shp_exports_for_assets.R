# Export shp files to upload as assets
## Temporal solution to automated asset generation

library(dplyr)
library(sf)
library(janitor)

# Reservoirs | ABMI ----
reservoirs <- st_read(dsn = here::here('data/HFI2021.gdb/HFI2021.gdb'),
                      layer = 'o01_Reservoirs_HFI_2021') |> 
        clean_names()

# Write shp for GEE
# write_sf(obj = reservoirs, dsn = "data/reservoirs.shp")

# Roads | ABMI ----
roads <- st_read(dsn = here::here('data/HFI2021.gdb/HFI2021.gdb'),
                 layer = 'o03_Roads_HFI_2021') |> 
        clean_names() |> 
        select(feature_ty, Shape)

# Write shp for GEE
# write_sf(obj = roads, dsn = "data/roads.shp")

# Residentials | ABMI ---- 
residentials <- st_read(dsn = here::here('data/HFI2021.gdb/HFI2021.gdb'),
                        layer = 'o15_Residentials_HFI_2021') |> 
        clean_names() |> 
        select(feature_ty, Shape)

# Write shp for GEE
# write_sf(obj = residentials, dsn = "data/residentials.shp")

# Industrials | ABMI ----
industrials <- st_read(dsn = here::here('data/HFI2021.gdb/HFI2021.gdb'),
                       layer = 'o08_Industrials_HFI_2021') |> 
        clean_names() |> 
        select(feature_ty, Shape)

# Write shp for GEE
# write_sf(obj = industrials, dsn = "data/industrials.shp")


# Fires shp for GEE
fires <- st_read(dsn = here::here('data/NFDB_poly/NFDB_poly_20210707.shp')) |> 
        clean_names() |> 
        filter(src_agency == "AB")

# Need to drop elevation, GDAL error if not
fires_2d <- st_zm(fires, drop = TRUE, what = "ZM")

# Write shp for GEE
# write_sf(obj = fires_2d, dsn = "data/fires.shp")



















