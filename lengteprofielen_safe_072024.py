import arcpy
arcpy.env.overwriteOutput = True
from arcpy.sa import *

arcpy.env.workspace = r"C:\Users\vince\Documents\ArcGIS\Projects\safe_lengteprofielen_072024\safe_lengteprofielen_072024.gdb"

# inputs
input_trajects = "testvak"
ahn4_raster = "https://tiles.arcgis.com/tiles/nSZVuSZjHpEZZbRo/arcgis/rest/services/Elevation_3D_RD/ImageServer"
raster_1 = r"C:\Users\vince\Documents\ArcGIS\Projects\safe ahn\safe ahn.gdb\safe_ahn4_200mbuffer"

# fields
ahn4_field = "ahn4"
raster_1_field = "raster1"

point_distance = 1 # m 

# werkdata
point_layer = "temp_pointlayer"


# generate points over lines
arcpy.management.GeneratePointsAlongLines(
    Input_Features=input_trajects,
    Output_Feature_Class=point_layer,
    Point_Placement="DISTANCE",
    Distance=f"{point_distance} Meters",
    Percentage=None,
    Include_End_Points="END_POINTS",
    Add_Chainage_Fields="ADD_CHAINAGE"
)

print ("points generated")

# extract values for points
arcpy.sa.ExtractMultiValuesToPoints(
    in_point_features=point_layer,
    in_rasters=f"{ahn4_raster} {ahn4_field};{raster_1} {raster_1_field}",
    bilinear_interpolate_values="NONE"
)

print ("values extracted")



