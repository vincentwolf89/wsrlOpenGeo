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
raster_prefix = "inputraster"

profile_length_river = 30 #m
profile_length_land = 30 #m
profile_interval = 20 #m
point_interval = 5 #m




def rewrite_rasters():

    arcpy.env.workspace = input_gdb
    arcpy.env.overwriteOutput = True

    # set environment to input
    input_rasters = arcpy.ListRasters("*")
    for raster in input_rasters:
        raster = str(raster)
        if raster.startswith(raster_prefix) == True:
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
        raster = str(raster)
        if raster.startswith(raster_prefix) == True:
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

            arcpy.AddField_management(profiles, "midpoint_x", "DOUBLE", 2, field_is_nullable="NULLABLE")
            arcpy.AddField_management(profiles, "midpoint_y", "DOUBLE", 2, field_is_nullable="NULLABLE")
            arcpy.AddField_management(profiles, "bearing_1", "DOUBLE", 2, field_is_nullable="NULLABLE")
            arcpy.AddField_management(profiles, "bearing_2", "DOUBLE", 2, field_is_nullable="NULLABLE")
            arcpy.AddField_management(profiles, "half_length", "DOUBLE", 2, field_is_nullable="NULLABLE")



def find_steepest_profile():
    arcpy.env.workspace = output_gdb
    arcpy.env.overwriteOutput = True
    output_rasters = arcpy.ListRasters("*")
    for raster in output_rasters:
        raster = str(raster)
        if raster.startswith(raster_prefix) == True:
            arcpy.management.CopyFeatures("profiles_{}".format(str(raster)), "profiles_test")
            profiles = "profiles_test"
            
            # calculate bearing 
            arcpy.management.CalculateGeometryAttributes(profiles, [["bearing_1", "LINE_BEARING"],["midpoint_x", "CENTROID_X"],["midpoint_y", "CENTROID_Y"]])
            arcpy.management.CalculateField(profiles, "bearing_2", "$feature.bearing_1-180", "ARCADE")
            arcpy.management.CalculateField(profiles, "half_length", "round(!SHAPE.LENGTH!/2)","PYTHON3")    
            # iterate over profiles:
            profile_cursor = arcpy.da.SearchCursor(profiles,['bearing_1','bearing_2','midpoint_x','midpoint_y','half_length','SHAPE@','profielnummer'])
            for row in profile_cursor:

                attempts = list(range(0,11))
                bearing = row[0]-90
                profile_number = row[6]
                profile = "testprofile"
                where = '"profielnummer" = {}'.format(profile_number)
                arcpy.Select_analysis(profiles, profile, where)

                profile_list = []
                for item in attempts:
                    arcpy.management.CalculateField(profile, "bearing_1", "'"+ str(round(bearing)) +"'", "PYTHON3")
                    arcpy.management.CalculateField(profile, "bearing_2", "'"+ str(round(bearing-180)) +"'", "PYTHON3")
                    
                    arcpy.BearingDistanceToLine_management(profile, "tester_1_{}".format(str(item)), "midpoint_x", "midpoint_y", distance_field="half_length",bearing_field="bearing_1")
                    arcpy.BearingDistanceToLine_management(profile, "tester_2_{}".format(str(item)), "midpoint_x", "midpoint_y", distance_field="half_length",bearing_field="bearing_2")
                    bearing += 18
                    print(bearing)


                    

                    arcpy.management.Merge(["tester_1_{}".format(str(item)),"tester_2_{}".format(str(item))],"templayer")
                    arcpy.management.Dissolve("templayer", "profile_{}".format(item))
                    
                    profile_list.append("profile_{}".format(item))

                arcpy.management.Merge(profile_list ,"profiles")
                # add code field
                arcpy.AddField_management("profiles", code, "DOUBLE", 2, field_is_nullable="NULLABLE")
                arcpy.AddField_management("profiles", "profielnummer", "DOUBLE", 2, field_is_nullable="NULLABLE")
                arcpy.management.CalculateField("profiles", code, "'code'", "PYTHON3")
                arcpy.management.CalculateField("profiles", "profielnummer", '!OBJECTID!', "PYTHON3")
                copy_trajectory_lr(trajectory,code,1)
                set_measurements_trajectory("profiles", trajectory, code, point_interval)

                
                
                break
       
rewrite_rasters()
profiles_part1()
# find_steepest_profile()
