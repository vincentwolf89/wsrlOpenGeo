import arcpy
arcpy.env.overwriteOutput = True
from arcpy.sa import *

arcpy.env.workspace = r"C:\Users\vince\Documents\ArcGIS\Projects\beoordeling ssh\beoordeling ssh.gdb"

input1 = r"C:\Users\vince\Documents\ArcGIS\Projects\beoordeling ssh\input\test_invoer.xlsx"
sheetInput1 = "Blad1"
tableFields = ["dp_van","dp_tot","offset_van","offset_tot"]
startIdField = "dp_van"
startOffsetField = "offset_van"
endIdField = "dp_tot"
endOffsetField = "offset_tot"


dikeTrajectory = "ssh_spst_trajectlijn"
dikeRefpoints = "merge_dp_ssh_spst"
route_field = "code"
route_tolerance = 15
id_field ="dijkvak"
dp_field = "rftident"

from_field ="dp_van"
till_field = "dp_tot"

def createDpRoutes():
    # split trajectory on dp
    arcpy.management.SplitLineAtPoint(dikeTrajectory, dikeRefpoints, "temp_trajectory_split", "{} Meters".format(route_tolerance))

    # create segment routes
    arcpy.AddField_management("temp_trajectory_split", "from_field", "DOUBLE", 2, field_is_nullable="NULLABLE")
    arcpy.AddField_management("temp_trajectory_split", "till_field", "DOUBLE", 2, field_is_nullable="NULLABLE")

    arcpy.management.CalculateField("temp_trajectory_split", "from_field", "0", "PYTHON3", '', "TEXT", "NO_ENFORCE_DOMAINS")
    arcpy.management.CalculateField("temp_trajectory_split", "till_field", "!Shape_Length!", "PYTHON3", '', "TEXT", "NO_ENFORCE_DOMAINS")

    arcpy.lr.CreateRoutes("temp_trajectory_split", "ORIG_SEQ", "temp_routes_trajectory", "TWO_FIELDS", "from_field", "till_field", "", "1","0", "IGNORE", "INDEX")

    # generate startpoints for splits
    arcpy.management.FeatureVerticesToPoints("temp_trajectory_split", "temp_startpoints", "START")
    # join startspoints to dp
    arcpy.analysis.SpatialJoin("temp_startpoints", dikeRefpoints, "temp_startpoints_ref", "JOIN_ONE_TO_ONE", "KEEP_ALL", "", "CLOSEST", None, '')

    # generate endpoints for splits
    arcpy.management.FeatureVerticesToPoints("temp_trajectory_split", "temp_endpoints", "END")
    # join endpoints to dp
    arcpy.analysis.SpatialJoin("temp_endpoints", dikeRefpoints, "temp_endpoints_ref", "JOIN_ONE_TO_ONE", "KEEP_ALL", "", "CLOSEST", None, '')

    # join id fields from refpoints to routes
    arcpy.management.JoinField("temp_routes_trajectory", "ORIG_SEQ", "temp_startpoints_ref", "ORIG_SEQ", "rftident", "NOT_USE_FM", None)
    arcpy.management.JoinField("temp_routes_trajectory", "ORIG_SEQ", "temp_endpoints_ref", "ORIG_SEQ", "rftident", "NOT_USE_FM", None)

    arcpy.management.AlterField("temp_routes_trajectory", "rftident", "start_id",clear_field_alias="CLEAR_ALIAS")
    arcpy.management.AlterField("temp_routes_trajectory", "rftident_1", "end_id",clear_field_alias="CLEAR_ALIAS")


    # get input excel and locate
    arcpy.conversion.ExcelToTable(input1, "tableInput1", sheetInput1, 1, '')

# loop through table rows:
tableCursor = arcpy.da.SearchCursor("tableInput1",tableFields)
for tableRow in tableCursor:

    # create templayer
    rowItem = tableRow[0]

    arcpy.conversion.ExportTable("tableInput1", "temp_tablerow", "{} = '{}'".format(startIdField,rowItem))

    arcpy.lr.MakeRouteEventLayer("temp_routes_trajectory", "start_id", "temp_tablerow", "{}; Point; {}".format(startIdField, startOffsetField), "temp_startpoint", None, "NO_ERROR_FIELD", "NO_ANGLE_FIELD", "NORMAL", "ANGLE", "LEFT", "POINT")
    arcpy.lr.MakeRouteEventLayer("temp_routes_trajectory", "end_id", "temp_tablerow", "{}; Point; {}".format(endIdField, endOffsetField), "temp_endpoint", None, "NO_ERROR_FIELD", "NO_ANGLE_FIELD", "NORMAL", "ANGLE", "LEFT", "POINT")
    arcpy.management.CopyFeatures("temp_startpoint", "temp_startpoint_segment")
    arcpy.management.CopyFeatures("temp_endpoint", "temp_endpoint_segment")

    # create line segment
    arcpy.management.Merge(["temp_startpoint_segment","temp_endpoint_segment"],"temp_merge_isectpoints")

    break


    
  



# make first point, make second point, create line segment, add segment to totals layer...