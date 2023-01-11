import arcpy
arcpy.env.overwriteOutput = True
from arcpy.sa import *

arcpy.env.workspace = r"C:\Users\vince\Documents\ArcGIS\Projects\beoordeling ssh\beoordeling ssh.gdb"
tempData =  "C:/Users/vince/Documents/ArcGIS/Projects/beoordeling ssh/tempData.gdb/"


dikeTrajectory = "ssh_spst_trajectlijn"
pointInterval = 10 # meters
pointSearchRadius = 1 # meters
codeField = "code"
oidField = "OBJECTID"
failureMechanisms = ["stbi_results", "stph_results"] # array with all fm

# trajectline to points
arcpy.management.GeneratePointsAlongLines(dikeTrajectory, "temp_trajectory_points", "DISTANCE", "{} Meters".format(pointInterval), None, None)

# split line at points
arcpy.management.SplitLineAtPoint(dikeTrajectory, "temp_trajectory_points", "temp_trajectory_splitted", "{} Meters".format(pointSearchRadius))

# midpoints for sections
arcpy.management.FeatureVerticesToPoints("temp_trajectory_splitted", "temp_trajectory_splitted_midpoints", "MID")

# iterate over midpoints, select all lines and iterate lines
segmentCursor = arcpy.da.UpdateCursor("temp_trajectory_splitted", ["OBJECTID"])
for segmentRow in segmentCursor:

    # create templayer
    oid = int(segmentRow[0])
    where = '"' + oidField + '" = ' + str(oid)
    temp_section = "temp_section"
    arcpy.Select_analysis("temp_trajectory_splitted", temp_section, where)

    # find intersecting failure mechanisms
    for fm in failureMechanisms:
        # spatial join temp_section to fm
        # check output and do calc considering rules

    
