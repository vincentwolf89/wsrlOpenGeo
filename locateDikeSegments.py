import arcpy
arcpy.env.overwriteOutput = True
from arcpy.sa import *

arcpy.env.workspace = r"C:\Users\vince\Documents\ArcGIS\Projects\schets nelle\schets nelle.gdb"

dike_segments = "testlaag_dijksegment_rd"
dike_trajectory = "trajectlijn_safe_rd"
dike_refpoints = "dijkpalen_safe_rd"
route_field = "code"
route_tolerance = 10
id_field ="id"
dp_field = "RFTIDENT"

from_field ="dp_van"
till_field = "dp_tot"

## create routes for dp :
# split trajectory on dp
arcpy.management.SplitLineAtPoint(dike_trajectory, dike_refpoints, "temp_trajectory_split", "{} Meters".format(route_tolerance))
# create segment routes
arcpy.lr.CreateRoutes("temp_trajectory_split", "ORIG_SEQ", "temp_routes_trajectory", "LENGTH", None, None, "UPPER_LEFT", 1, 0, "IGNORE", "INDEX")

# generate startpoints for splits
arcpy.management.FeatureVerticesToPoints("temp_trajectory_split", "temp_startpoints", "START")
# join startspoints to dp
arcpy.analysis.SpatialJoin("temp_startpoints", dike_refpoints, "temp_startpoints_ref", "JOIN_ONE_TO_ONE", "KEEP_ALL", "", "CLOSEST", None, '')

# generate endpoints for splits
arcpy.management.FeatureVerticesToPoints("temp_trajectory_split", "temp_endpoints", "END")
# join endpoints to dp
arcpy.analysis.SpatialJoin("temp_endpoints", dike_refpoints, "temp_endpoints_ref", "JOIN_ONE_TO_ONE", "KEEP_ALL", "", "CLOSEST", None, '')

# join id fields from refpoints to routes
arcpy.management.JoinField("temp_routes_trajectory", "ORIG_SEQ", "temp_startpoints_ref", "ORIG_SEQ", "rftident", "NOT_USE_FM", None)
arcpy.management.JoinField("temp_routes_trajectory", "ORIG_SEQ", "temp_endpoints_ref", "ORIG_SEQ", "rftident", "NOT_USE_FM", None)

arcpy.management.AlterField("temp_routes_trajectory", "rftident", "start_id", '', "TEXT", 24, "NULLABLE", "CLEAR_ALIAS")
arcpy.management.AlterField("temp_routes_trajectory", "rftident_1", "end_id", '', "TEXT", 24, "NULLABLE", "CLEAR_ALIAS")

# create start and enpoints for for dike segments
arcpy.management.FeatureVerticesToPoints(dike_segments, "temp_startpoints_segments", "START")
arcpy.management.FeatureVerticesToPoints(dike_segments, "temp_endpoints_segments", "END")

# locate endpoints along routes
arcpy.lr.LocateFeaturesAlongRoutes("temp_startpoints_segments", "temp_routes_trajectory", "ORIG_SEQ", "{} Meters".format(route_tolerance), "temp_located_startpoints", "RID; Point; MEAS", "FIRST", "DISTANCE", "ZERO", "FIELDS", "M_DIRECTON")
arcpy.lr.LocateFeaturesAlongRoutes("temp_endpoints_segments", "temp_routes_trajectory", "ORIG_SEQ", "{} Meters".format(route_tolerance), "temp_located_endpoints", "RID; Point; MEAS", "FIRST", "DISTANCE", "ZERO", "FIELDS", "M_DIRECTON")

arcpy.management.JoinField("temp_located_startpoints", "RID", "temp_routes_trajectory", "ORIG_SEQ", "start_id", "NOT_USE_FM", None)
arcpy.management.JoinField("temp_located_endpoints", "RID", "temp_routes_trajectory", "ORIG_SEQ", "end_id", "NOT_USE_FM", None)

# join meas from locate
arcpy.management.JoinField("temp_startpoints_segments", id_field, "temp_located_startpoints", "ORIG_FID", "MEAS", "NOT_USE_FM", None)
arcpy.management.JoinField("temp_endpoints_segments", id_field, "temp_located_endpoints", "ORIG_FID", "MEAS", "NOT_USE_FM", None)

# join meas fields to dike segments
arcpy.management.CopyFeatures(dike_segments, "temp_ouput_segments")

arcpy.management.JoinField("temp_ouput_segments", id_field, "temp_located_startpoints", id_field, "start_id", "NOT_USE_FM", None)
arcpy.management.JoinField("temp_ouput_segments", id_field, "temp_located_endpoints", id_field, "end_id", "NOT_USE_FM", None)

arcpy.management.AlterField("temp_ouput_segments", "MEAS", "start_distance", '', "DOUBLE", 8, "NULLABLE", "DO_NOT_CLEAR")
arcpy.management.AlterField("temp_ouput_segments", "MEAS_1", "end_distance", '', "DOUBLE", 8, "NULLABLE", "DO_NOT_CLEAR")

# add new fields with correct name
arcpy.AddField_management("temp_ouput_segments", from_field, "TEXT", 2)
arcpy.AddField_management("temp_ouput_segments", till_field, "TEXT", 2)

arcpy.management.CalculateField("temp_ouput_segments", from_field, "$feature.start_id + '+'+ Text(Round($feature.start_distance,0))", "ARCADE")
arcpy.management.CalculateField("temp_ouput_segments", till_field, "$feature.end_id + '+'+ Text(Round($feature.end_distance,0))", "ARCADE")


