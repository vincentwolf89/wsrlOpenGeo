import arcpy
import numpy as np
import pandas as pd
import os
from itertools import groupby
from base import *
arcpy.env.overwriteOutput = True

# params
grid_size = 5 #m
temp_gdb = r"C:\Users\vince\Documents\ArcGIS\Projects\rasters willem oktober\temp.gdb"#database
input_gdb = r"C:\Users\vince\Documents\ArcGIS\Projects\rasters willem oktober\input_rasters.gdb"#database
output_gdb =  r"C:\Users\vince\Documents\ArcGIS\Projects\rasters willem oktober\output_rasters.gdb"#database
trajectory = r"C:\Users\vince\Documents\ArcGIS\Projects\rasters willem oktober\input_rasters.gdb\trajectlijn"
code = "code"
fieldnames =['profielnummer', 'afstand', 'z_ahn', 'x', 'y']
xls_outputloc = r"C:\Users\vince\Desktop\ssh_output\output_xlsx"
raster_prefix = "KD"

profile_length_river = 100 #m
profile_length_land = 100 #m
profile_interval = 20 #m
point_interval = 5 #m
extension_river = 30 #m

def project_rasters():
    arcpy.env.workspace = temp_gdb
    arcpy.env.overwriteOutput = True

    # set environment to input
    input_rasters = r"C:\Users\vince\Documents\ArcGIS\Projects\rasters willem oktober\rasters_los"

    for raster_name in os.listdir(input_rasters):
        raster = input_rasters+"\{}".format(raster_name)
        output_raster = raster_name.split("-")[2][0:11]
    
        arcpy.management.ProjectRaster(raster, output_raster, 'PROJCS["RD_New",GEOGCS["GCS_Amersfoort",DATUM["D_Amersfoort",SPHEROID["Bessel_1841",6377397.155,299.1528128]],PRIMEM["Greenwich",0.0],UNIT["Degree",0.0174532925199433]],PROJECTION["Double_Stereographic"],PARAMETER["False_Easting",155000.0],PARAMETER["False_Northing",463000.0],PARAMETER["Central_Meridian",5.38763888888889],PARAMETER["Scale_Factor",0.9999079],PARAMETER["Latitude_Of_Origin",52.15616055555555],UNIT["Meter",1.0]]', "NEAREST", "5 5", None, None, 'GEOGCS["GCS_WGS_1984",DATUM["D_WGS_1984",SPHEROID["WGS_1984",6378137.0,298.257223563]],PRIMEM["Greenwich",0.0],UNIT["Degree",0.0174532925199433]]', "NO_VERTICAL")



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
            

            print (raster)
           



def find_steepest_profile():
    arcpy.env.workspace = output_gdb
    arcpy.env.overwriteOutput = True
    output_rasters = arcpy.ListRasters("*")
    for raster in output_rasters:
        raster = str(raster)
        if raster.startswith(raster_prefix) == True:
            arcpy.management.CopyFeatures("profiles_{}".format(str(raster)), "profiles_test")

            # create feature class and insertcursor
            max_slope_profiles = "max_slope_profiles_"+str(raster)
            sref = arcpy.Describe(raster).spatialReference
            arcpy.CreateFeatureclass_management(output_gdb, max_slope_profiles, geometry_type="POLYLINE", spatial_reference= sref)
            max_slope_insert_fields = ['SHAPE@','profielnummer', 'slope', 'bearing', 'bearing_dike']
            for field in max_slope_insert_fields:
                if field != "SHAPE@":
                    arcpy.AddField_management(max_slope_profiles, field , "DOUBLE", 2, field_is_nullable="NULLABLE")
            
            max_slope_insert_cursor = arcpy.da.InsertCursor(max_slope_profiles, max_slope_insert_fields)


            
            profiles = "profiles_test"
            arcpy.AddField_management(profiles, "extension_river", "DOUBLE", 2, field_is_nullable="NULLABLE")
            arcpy.management.CalculateField(profiles, "extension_river", "'{}'".format(extension_river),"PYTHON3")  
            
            # calculate bearing 
            arcpy.management.CalculateGeometryAttributes(profiles, [["bearing_1", "LINE_BEARING"],["midpoint_x", "CENTROID_X"],["midpoint_y", "CENTROID_Y"]])
            # arcpy.management.CalculateField(profiles, "bearing_2", "$feature.bearing_1-180", "ARCADE")
             
            # iterate over profiles:
            profile_cursor = arcpy.da.SearchCursor(profiles,['bearing_1','bearing_2','midpoint_x','midpoint_y','extension_river','SHAPE@','profielnummer'])
            for row in profile_cursor:
                
                attempts = list(range(0,9))
                profile_main_bearing = row[0]
                bearing = row[0]-90+18

                if bearing >= 360:
                    bearing = bearing-360

                profile_main_number = row[6]
                profile = "testprofile"
                where = '"profielnummer" = {}'.format(profile_main_number)
                arcpy.Select_analysis(profiles, profile, where)

                profile_list = []
                for item in attempts:
                    arcpy.management.CalculateField(profile, "bearing_1", "'"+ str(round(bearing)) +"'", "PYTHON3")
                    # arcpy.management.CalculateField(profile, "bearing_2", "'"+ str(round(bearing-180)) +"'", "PYTHON3")
                    
                    arcpy.BearingDistanceToLine_management(profile, "profile_{}".format(item), "midpoint_x", "midpoint_y", distance_field="extension_river",bearing_field="bearing_1")
                    # arcpy.BearingDistanceToLine_management(profile, "tester_2_{}".format(str(item)), "midpoint_x", "midpoint_y", distance_field="half_length",bearing_field="bearing_2")
                    bearing += 18

                    if bearing >= 360:
                        bearing = bearing-360
                    print(bearing)


                    # arcpy.management.Merge(["tester_1_{}".format(str(item)),"tester_2_{}".format(str(item))],"templayer")
                    # arcpy.management.Dissolve("templayer", "profile_{}".format(item))
                    
                    profile_list.append("profile_{}".format(item))

                max_slope_profiles = "max_slope_profiles"

                arcpy.management.Merge(profile_list , max_slope_profiles)
                # add code field
                arcpy.AddField_management(max_slope_profiles, code, "DOUBLE", 2, field_is_nullable="NULLABLE")
                arcpy.AddField_management(max_slope_profiles, "profielnummer", "DOUBLE", 2, field_is_nullable="NULLABLE")
                
                arcpy.management.CalculateField(max_slope_profiles, code, "'code'", "PYTHON3")
                arcpy.management.CalculateField(max_slope_profiles, "profielnummer", '!OBJECTID!', "PYTHON3")
                copy_trajectory_lr(trajectory,code,1)
                set_measurements_trajectory(max_slope_profiles, trajectory, code, point_interval)

                input_points = "punten_profielen"
                output_points = "points_profiles_z"
                extract_z_arcpy(input_points,output_points,raster)

                # find steepest profile
                slopes_list = []
                slope_cursor = arcpy.da.SearchCursor(output_points,['profielnummer','afstand','z_ahn'],sql_clause=(None, 'ORDER BY profielnummer, afstand'))
                for profile_number, group in groupby(slope_cursor, lambda x: x[0]):
    
                    x_list = []
                    z_list = []
                    for slope_row in group:
                        x_list.append(round(slope_row[1],2))
                        z_list.append(round(slope_row[2],2))


                    x_array= np.array(x_list)
                    z_array= np.array(z_list)
                    n = np.size(x_array)
                    x_mean = np.mean(x_array)
                    z_mean = np.mean(z_array)
                    x_mean,z_mean
                
                    Sxy = np.sum(x_array*z_array)- n*x_mean*z_mean
                    Sxx = np.sum(x_array*x_array)-n*x_mean*x_mean
                
                    slope = Sxy/Sxx
                    slopes_list.append([profile_number,abs(slope)])
                
                slope_df = pd.DataFrame(slopes_list, columns=['profile_number', 'slope'])
                # print (slope_df)
                max_slope = slope_df[slope_df.slope == slope_df.slope.max()].iloc[0]['slope']
                profile_max_slope = slope_df[slope_df.slope == slope_df.slope.max()].iloc[0]['profile_number']

                # get remaining profile, delete others
                arcpy.AddField_management(max_slope_profiles, "slope", "DOUBLE", 2, field_is_nullable="NULLABLE")

                max_profile_cursor = arcpy.da.UpdateCursor(max_slope_profiles,['profielnummer','slope'])
                for profile_row in max_profile_cursor:
                    if int(profile_row[0]) == int(profile_max_slope):
                        profile_row[1] = max_slope
                        max_profile_cursor.updateRow(profile_row)
                    else:
                        max_profile_cursor.deleteRow()
                del max_profile_cursor


                # find the angle
                arcpy.AddField_management(max_slope_profiles, "bearing", "DOUBLE", 2, field_is_nullable="NULLABLE")
                arcpy.AddField_management(max_slope_profiles, "bearing_dike", "DOUBLE", 2, field_is_nullable="NULLABLE")
                arcpy.management.CalculateGeometryAttributes(max_slope_profiles, [["bearing", "LINE_BEARING"]])
                bearing_profile_cursor = arcpy.da.UpdateCursor(max_slope_profiles,['profielnummer','slope','bearing','bearing_dike','SHAPE@'])
                for profile_row in bearing_profile_cursor:
                    profile_bearing = profile_row[2]
                    if profile_bearing > 180:
                        profile_bearing = abs(profile_bearing-360)
                    
                    if profile_main_bearing > 180:
                        profile_main_bearing = abs(profile_main_bearing-360)

                    bearing_difference = abs(profile_bearing-profile_main_bearing)
                    profile_row[3] = 90-bearing_difference
                    bearing_profile_cursor.updateRow(profile_row)


                    insertRow = (profile_row[4],profile_main_number,profile_row[1],profile_row[2],profile_row[3])

                
                del bearing_profile_cursor
                max_slope_insert_cursor.insertRow(insertRow)
                


                
                
                break

            break

# project_rasters()       
# rewrite_rasters()
# profiles_part1()
find_steepest_profile()
