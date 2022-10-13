import arcpy
import numpy as np
import pandas as pd
from base import *
arcpy.env.overwriteOutput = True

# params
grid_size = 5 #m
input_gdb = r"C:\Users\vince\Documents\ArcGIS\Projects\rasters willem oktober\input_rasters.gdb"#database
output_gdb =  r"C:\Users\vince\Documents\ArcGIS\Projects\rasters willem oktober\output_rasters.gdb"#database
trajectory = r"C:\Users\vince\Documents\ArcGIS\Projects\rasters willem oktober\input_rasters.gdb\trajectlijn_demo"
code = "code"
fieldnames =['profielnummer', 'afstand', 'z_ahn', 'x', 'y']
xls_outputloc = r"C:\Users\vince\Desktop\ssh_output"

profile_length_river = 30 #m
profile_length_land = 30 #m
profile_interval = 25 #m
point_interval = 5 #m

def rewrite_rasters():

    arcpy.env.workspace = input_gdb
    arcpy.env.overwriteOutput = True

    # set environment to input
    input_rasters = arcpy.ListRasters("*")
    for raster in input_rasters:
        raster = str(raster)
        raster_output = raster+"_{}".format(str(grid_size)+"m")
        # raster naar punten vertalen
        arcpy.conversion.RasterToPoint(raster, "tempraster_points", "Value")
        # # punten interpoleren met IDW en gewenste gridgrootte
        arcpy.ddd.Idw("tempraster_points", "grid_code", output_gdb+"/"+raster_output, grid_size, 2, "VARIABLE 12", None)

    print ("raster written to grid size: {}".format(grid_size))

def profiles_part1():
    # switch environment to ouput
    arcpy.env.workspace = output_gdb
    arcpy.env.overwriteOutput = True
    output_rasters = arcpy.ListRasters("*")
    for raster in output_rasters:

        profiles = "profiles_{}".format(str(raster))
        input_points = "punten_profielen"
        output_points = "points_profiles_z"
        excel = xls_outputloc+"/"+ "output_profiles_{}".format(str(raster)+".xlsx")
        # profielen trekken
        generate_profiles(profile_interval, profile_length_land, profile_length_river, trajectory, code, profiles)

        copy_trajectory_lr(trajectory,code,10)

        set_measurements_trajectory(profiles, trajectory, code, point_interval)

        extract_z_arcpy(input_points,output_points,raster)

        add_xy(output_points, code,trajectory)

        excelWriterTraject(output_points, excel, fieldnames)


profiles_part1()