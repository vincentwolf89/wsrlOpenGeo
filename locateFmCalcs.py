import arcpy
arcpy.env.overwriteOutput = True
from arcpy.sa import *

arcpy.env.workspace = r"C:\Users\vince\Documents\ArcGIS\Projects\beoordeling ssh\beoordeling ssh.gdb"
tempData =  "C:/Users/vince/Documents/ArcGIS/Projects/beoordeling ssh/tempData.gdb/"

input1 = r"C:\Users\vince\Documents\ArcGIS\Projects\beoordeling ssh\input\stbi\input_stbi_jan_2023.xlsx"
sheetInput1 = "STBI"
oordeelField = "cat_oordeel_2075"
tableFields = ["dp_van","dp_tot","offset_van","offset_tot",oordeelField,"dijkvak"]
startIdField = "dp_van"
startOffsetField = "offset_van"
endIdField = "dp_tot"
endOffsetField = "offset_tot"
eindOordeelLijn = "oordeel_stbi_jan_2023"
categoriesInSufficient = ["IV","V","VI"]


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


def calcBase():   
    # get input excel and loop through
    arcpy.conversion.ExcelToTable(input1, "tableInput1", sheetInput1, 1, '')
    tableCursor = arcpy.da.SearchCursor("tableInput1",tableFields)

    segments = []
    count = 0
    for tableRow in tableCursor:

        arcpy.conversion.ExportTable("tableInput1", r"C:\Users\vince\Documents\ArcGIS\Projects\beoordeling ssh\beoordeling ssh.gdb\tableInput1_ExportTable", "dp_van = 'DR183.' And offset_van = 0", "NOT_USE_ALIAS", 'dijkvak "dijkvak" true true false 255 Text 0 0,First,#,tableInput1,dijkvak,0,255;dp_van "dp_van" true true false 255 Text 0 0,First,#,tableInput1,dp_van,0,255;dp_tot "dp_tot" true true false 255 Text 0 0,First,#,tableInput1,dp_tot,0,255;offset_van "offset_van" true true false 4 Long 0 0,First,#,tableInput1,offset_van,-1,-1;offset_tot "offset_tot" true true false 4 Long 0 0,First,#,tableInput1,offset_tot,-1,-1;cat_oordeel_2075 "cat_oordeel_2075" true true false 255 Text 0 0,First,#,tableInput1,cat_oordeel_2075,0,255', None)

        # create templayer
        rowIdStart = tableRow[0]
        rowOffsetStart = tableRow[2]

        # arcpy.conversion.ExportTable("tableInput1", "temp_tablerow", "{} = '{}'".format(startIdField,rowIdStart))
        arcpy.conversion.ExportTable("tableInput1", "temp_tablerow", "{} = '{}' And {} = {}".format(startIdField,rowIdStart,startOffsetField,rowOffsetStart))

        arcpy.lr.MakeRouteEventLayer("temp_routes_trajectory", "start_id", "temp_tablerow", "{}; Point; {}".format(startIdField, startOffsetField), "temp_startpoint", None, "NO_ERROR_FIELD", "NO_ANGLE_FIELD", "NORMAL", "ANGLE", "LEFT", "POINT")
        arcpy.lr.MakeRouteEventLayer("temp_routes_trajectory", "start_id", "temp_tablerow", "{}; Point; {}".format(endIdField, endOffsetField), "temp_endpoint", None, "NO_ERROR_FIELD", "NO_ANGLE_FIELD", "NORMAL", "ANGLE", "LEFT", "POINT")
        arcpy.management.CopyFeatures("temp_startpoint", "startpoint_segment")
        arcpy.management.CopyFeatures("temp_endpoint", "endpoint_segment")

        # create line segment
        arcpy.management.Merge(["startpoint_segment","endpoint_segment"], "temp_table_row_points")
        # create splits
        arcpy.management.SplitLineAtPoint(dikeTrajectory, "temp_table_row_points", "temp_table_row_line_total", "0.5 Meters")
        
        # copy row and create offset point for isect locating
        # arcpy.conversion.ExportTable("tableInput1", "temp_tablerow_offset_locator", "{} = '{}'".format(startIdField,rowIdStart))
        arcpy.conversion.ExportTable("tableInput1", "temp_tablerow_offset_locator", "{} = '{}' And {} = {}".format(startIdField,rowIdStart,startOffsetField,rowOffsetStart))
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
        arcpy.management.AddJoin("templayer", "code", "temp_tablerow", "OBJECTID", "KEEP_ALL", "NO_INDEX_JOIN_FIELDS")
        segment = "{}tablerow_{}".format(tempData,count)
        arcpy.CopyFeatures_management("templayer", segment)
        # add to segments
        segments.append(segment)
        count += 1

    # merge segments
    arcpy.management.Merge(segments, eindOordeelLijn)
    arcpy.management.AlterField(eindOordeelLijn, "temp_tablerow_{}".format(oordeelField), oordeelField)

def calcFinal():
    existingFields = arcpy.ListFields(eindOordeelLijn)
    for field in existingFields:
        if field.name == "eindoordeel_final":
            pass
        else:
             arcpy.AddField_management(eindOordeelLijn, "eindoordeel_final", "TEXT", 2)

    oordeelCursor = arcpy.da.UpdateCursor(eindOordeelLijn,[oordeelField,"eindoordeel_final"])
    for oordeelRow in oordeelCursor:
        finalOordeel = "voldoende"
        for oordeel in categoriesInSufficient:
            
            if oordeelRow[0].startswith(oordeel):
                finalOordeel = "onvoldoende"
                break

        oordeelRow[1] = finalOordeel
        oordeelCursor.updateRow(oordeelRow)


calcBase()
calcFinal()



