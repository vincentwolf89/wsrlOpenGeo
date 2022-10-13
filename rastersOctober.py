import arcpy
import numpy as np
import pandas as pd
arcpy.env.overwriteOutput = True

# params
grid_size = 5 #m
input_rasters = r"C:\Users\vince\Documents\ArcGIS\Projects\rasters willem oktober\input_rasters.gdb "#database
output_rasters =  r"C:\Users\vince\Documents\ArcGIS\Projects\rasters willem oktober\output_rasters.gdb "#database

profile_length_river = 30 #m
profile_length_land = 30 #m
profile_interval = 25 #m

arcpy.env.workspace = input_rasters

rasters = arcpy.ListRasters("*")
for raster in rasters:
    raster = str(raster)
    raster_output = raster+"_{}".format(str(grid_size)+"m")
    # raster naar punten vertalen
    arcpy.conversion.RasterToPoint(raster, "tempraster_points", "Value")
    # # punten interpoleren met IDW en gewenste gridgrootte
    arcpy.ddd.Idw("tempraster_points", "grid_code", output_rasters+"/"+raster_output, grid_size, 2, "VARIABLE 12", None)

# # profielen trekken
# generate_profiles(profiel_interval,profiel_lengte_land,profiel_lengte_rivier,trajectlijn,code,5,profielen)

# copy_trajectory_lr(trajectlijn,code,10)

# set_measurements_trajectory(profielen,trajectlijn,code,stapgrootte_punten,10)

# extract_z_arcpy(invoerpunten,uitvoerpunten,raster)

# add_xy(uitvoerpunten, code,trajectlijn)

# excelWriterTraject(uitvoerpunten,excel,veldnamen)


#... 