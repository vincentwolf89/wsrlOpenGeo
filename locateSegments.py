import arcpy
arcpy.env.overwriteOutput = True
from arcpy.sa import *

arcpy.env.workspace = r"C:\Users\vince\Mijn Drive\WSRL\safe_data\safe_data\safe_data.gdb"
# safe_priovakken_2022_nieuw_rd
dike_segments = "templayer"
dike_trajectory = "trajectlijn_safe_rd"
dike_refpoints = "dijkpalen_safe_rd"
route_field = "code"
route_tolerance = 15 # normal 15
id_field ="OBJECTID"
dp_field = "RFTIDENT"

from_field ="dp_van"
till_field = "dp_tot"

## create routes for dp :
# split trajectory on dp
arcpy.management.SplitLineAtPoint(dike_trajectory, dike_refpoints, "temp_trajectory_split", "{} Meters".format(route_tolerance))

# create segment routes
arcpy.AddField_management("temp_trajectory_split", "from_field", "DOUBLE", 2, field_is_nullable="NULLABLE")
arcpy.AddField_management("temp_trajectory_split", "till_field", "DOUBLE", 2, field_is_nullable="NULLABLE")

arcpy.management.CalculateField("temp_trajectory_split", "from_field", "0", "PYTHON3", '', "TEXT", "NO_ENFORCE_DOMAINS")
arcpy.management.CalculateField("temp_trajectory_split", "till_field", "!Shape_Length!", "PYTHON3", '', "TEXT", "NO_ENFORCE_DOMAINS")

arcpy.lr.CreateRoutes("temp_trajectory_split", "ORIG_SEQ", "temp_routes_trajectory", "TWO_FIELDS", "from_field", "till_field", "", "1","0", "IGNORE", "INDEX")

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


# join meas and RID from locate
arcpy.management.JoinField("temp_startpoints_segments", id_field, "temp_located_startpoints", id_field, "RID;MEAS", "NOT_USE_FM", None)
arcpy.management.JoinField("temp_endpoints_segments", id_field, "temp_located_endpoints", id_field, "RID;MEAS", "NOT_USE_FM", None)


arcpy.management.JoinField("temp_startpoints_segments", "RID", "temp_routes_trajectory", "ORIG_SEQ", "start_id", "NOT_USE_FM", None)
arcpy.management.JoinField("temp_endpoints_segments", "RID", "temp_routes_trajectory", "ORIG_SEQ", "start_id", "NOT_USE_FM", None)

# do some renaming
arcpy.management.AlterField("temp_startpoints_segments", "MEAS", "start_distance", '', "DOUBLE", 8, "NULLABLE", "CLEAR_ALIAS")
arcpy.management.AlterField("temp_endpoints_segments", "MEAS", "end_distance", '', "DOUBLE", 8, "NULLABLE", "CLEAR_ALIAS")
arcpy.management.AlterField("temp_endpoints_segments", "start_id", "end_id", '', "TEXT", 24, "NULLABLE", "CLEAR_ALIAS")

# join meas fields to dike segments
arcpy.management.CopyFeatures(dike_segments, "temp_ouput_segments")

arcpy.management.JoinField("temp_ouput_segments", id_field, "temp_startpoints_segments", id_field, "start_id;start_distance", "NOT_USE_FM", None)
arcpy.management.JoinField("temp_ouput_segments", id_field, "temp_endpoints_segments", id_field, "end_id;end_distance", "NOT_USE_FM", None)

# # add new fields with correct name
arcpy.AddField_management("temp_ouput_segments", from_field, "TEXT", 2)
arcpy.AddField_management("temp_ouput_segments", till_field, "TEXT", 2)

arcpy.management.CalculateField("temp_ouput_segments", from_field, "$feature.start_id + '+'+ Text(Round($feature.start_distance,0))", "ARCADE")
arcpy.management.CalculateField("temp_ouput_segments", till_field, "$feature.end_id + '+'+ Text(Round($feature.end_distance,0))", "ARCADE")


# join fields to original featureclass
arcpy.management.JoinField(dike_segments, id_field, "temp_ouput_segments", id_field, "dp_van;dp_tot", "NOT_USE_FM", None)
print ("done")
