import arcpy
arcpy.env.overwriteOutput = True
from arcpy.sa import *

arcpy.env.workspace = r"C:\Users\vince\Documents\ArcGIS\Projects\Weurt-Deest\Weurt-Deest.gdb"
tempData =  "C:/Users/vince/Documents/ArcGIS/Projects/Weurt-Deest/tempdata.gdb/"

input1 = r"C:\Users\vince\Documents\ArcGIS\Projects\beoordeling ssh\input\stbi\input_stbi_maart_2023.xlsx"
sheetInput1 = "invoer_gis"

inTable = "wede_stph"
nameField = "stph_val"
tableFields = ["dp_van","dp_tot","offset_van","offset_tot",nameField]
startIdField = "dp_van"
startOffsetField = "offset_van"
endIdField = "dp_tot"
endOffsetField = "offset_tot"
eindOordeelLijn = "stph_testvakken"



dikeTrajectory = "trajectlijn_wd"
dikeRefpoints = "dp_wd"
route_field = "code" # add this to table!!
route_tolerance = 30
id_field ="dijkvak"
dp_field = "dp_van"

from_field ="dp_van"
till_field = "dp_tot"

prefixes_to_remove = ["temp_tablerow_", "test_segment_"]

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
    arcpy.management.JoinField("temp_routes_trajectory", "ORIG_SEQ", "temp_startpoints_ref", "ORIG_SEQ", dp_field, "NOT_USE_FM", None)
    arcpy.management.JoinField("temp_routes_trajectory", "ORIG_SEQ", "temp_endpoints_ref", "ORIG_SEQ", dp_field, "NOT_USE_FM", None)

    arcpy.management.AlterField("temp_routes_trajectory", dp_field, "start_id",clear_field_alias="CLEAR_ALIAS")
    arcpy.management.AlterField("temp_routes_trajectory", "{}_1".format(dp_field), "end_id",clear_field_alias="CLEAR_ALIAS")


def calcBase():   
    tableCursor = arcpy.da.SearchCursor(inTable,tableFields)

    segments = []
    count = 0
    for tableRow in tableCursor:

        # create templayer
        rowIdStart = tableRow[0]
        rowOffsetStart = tableRow[2]
        where = "{} = '{}' And {} = {}".format(startIdField,rowIdStart,startOffsetField,rowOffsetStart)
        print (where)

        arcpy.conversion.ExportTable(inTable, "temp_tablerow", where)

        arcpy.lr.MakeRouteEventLayer("temp_routes_trajectory", "start_id", "temp_tablerow", "{}; Point; {}".format(startIdField, startOffsetField), "temp_startpoint", None, "NO_ERROR_FIELD", "NO_ANGLE_FIELD", "NORMAL", "ANGLE", "LEFT", "POINT")
        arcpy.lr.MakeRouteEventLayer("temp_routes_trajectory", "start_id", "temp_tablerow", "{}; Point; {}".format(endIdField, endOffsetField), "temp_endpoint", None, "NO_ERROR_FIELD", "NO_ANGLE_FIELD", "NORMAL", "ANGLE", "LEFT", "POINT")
        arcpy.management.CopyFeatures("temp_startpoint", "startpoint_segment")
        arcpy.management.CopyFeatures("temp_endpoint", "endpoint_segment")

        # create line segment
        arcpy.management.Merge(["startpoint_segment","endpoint_segment"], "temp_table_row_points")
        # create splits
        arcpy.management.SplitLineAtPoint(dikeTrajectory, "temp_table_row_points", "temp_table_row_line_total", "0.5 Meters")
        
        # copy row and create offset point for isect locating
        arcpy.conversion.ExportTable(inTable, "temp_tablerow_offset_locator", "{} = '{}' And {} = {}".format(startIdField,rowIdStart,startOffsetField,rowOffsetStart))
        tempCursor = arcpy.da.UpdateCursor("temp_tablerow_offset_locator", [startOffsetField])
        for tempRow in tempCursor:
            startOffsetPlus = tempRow[0]+1
            tempRow[0] = startOffsetPlus
            tempCursor.updateRow(tempRow)

        del tempCursor
        arcpy.lr.MakeRouteEventLayer("temp_routes_trajectory", "start_id", "temp_tablerow_offset_locator", "{}; Point; {}".format(startIdField, startOffsetField), "temp_startpoint_offset_locator", None, "NO_ERROR_FIELD", "NO_ANGLE_FIELD", "NORMAL", "ANGLE", "LEFT", "POINT")
        arcpy.management.CopyFeatures("temp_startpoint_offset_locator", "startpoint_offset_locator")

        arcpy.management.MakeFeatureLayer("temp_table_row_line_total", "templayer")
        arcpy.management.SelectLayerByLocation("templayer", "INTERSECT", "startpoint_offset_locator", None, "NEW_SELECTION", "NOT_INVERT")
        arcpy.CopyFeatures_management("templayer", "test_segment")
        # join attributes from tablerow
        arcpy.management.MakeFeatureLayer("test_segment", "templayer")
        arcpy.management.AddJoin("templayer", route_field, "temp_tablerow", "OBJECTID", "KEEP_ALL", "NO_INDEX_JOIN_FIELDS")
        segment = "{}tablerow_{}".format(tempData,count)

        print (segment)
        arcpy.management.CopyFeatures("templayer", segment)
        # add to segments
        segments.append(segment)
        count += 1

        print (startOffsetPlus, count)
        # break



    # merge segments
    arcpy.management.Merge(segments, eindOordeelLijn)

    
def removePrefix():
    # remove prefix from fields
    # Get the fields of the layer
    fields = arcpy.ListFields(eindOordeelLijn)

    # Iterate over each field, rename it without the first word if applicable
    for field in fields:
        original_name = field.name
        
        # Check if the field name starts with any of the specified prefixes
        new_name = original_name
        for prefix in prefixes_to_remove:
            if original_name.startswith(prefix):
                # Remove the prefix by slicing it out
                new_name = original_name[len(prefix):]
                break  # Exit the loop once a prefix is removed
        
        # Rename the field if a prefix was removed
        if new_name != original_name:
            try:
                arcpy.AlterField_management(eindOordeelLijn, original_name, new_name)
                print(f"Renamed '{original_name}' to '{new_name}'")
            except Exception as e:
                print(f"Could not rename '{original_name}': {e}")
                arcpy.DeleteField_management(eindOordeelLijn, original_name)
        else:
            print(f"Skipping '{original_name}' (no matching prefix found)")

# createDpRoutes()
# calcBase()
removePrefix()




