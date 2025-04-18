import arcpy
arcpy.env.overwriteOutput = True
# from arcpy.sa import *

arcpy.env.workspace = r"C:\Users\vince\Documents\ArcGIS\Projects\beoordeling ssh\beoordeling ssh.gdb"
tempData =  "C:/Users/vince/Documents/ArcGIS/Projects/beoordeling ssh/tempData.gdb/"


dikeTrajectory = "deeltraject_d_ssh_test" #"ssh_spst_traject"
pointInterval = 20 # meters 
pointSearchRadius = 1 # meters
codeField = "code"
oidField = "OBJECTID_1"
failureMechanisms = ["STPH"] # array with all fm as line input
scorefield = "eindoordeel"
insufficientValue = "onvoldoende"
endCalcName = "eindoordeel_gecombineerd_27112024"

endScorefield = "eindoordeel_totaal"

# trajectline to points
arcpy.management.GeneratePointsAlongLines(dikeTrajectory, "temp_trajectory_points", "DISTANCE", "{} Meters".format(pointInterval), None, None)

# split line at points
arcpy.management.SplitLineAtPoint(dikeTrajectory, "temp_trajectory_points", "temp_trajectory_splitted", "{} Meters".format(pointSearchRadius))


arcpy.AddField_management("temp_trajectory_splitted", endScorefield, "TEXT", 2)
# iterate over midpoints, select all lines and iterate lines
segmentCursor = arcpy.da.UpdateCursor("temp_trajectory_splitted", [oidField, endScorefield])
for segmentRow in segmentCursor:

    # create templayer
    oid = int(segmentRow[0])
    where = '"' + oidField + '" = ' + str(oid)
    temp_section = "temp_section"
    arcpy.Select_analysis("temp_trajectory_splitted", temp_section, where)

    # create midpoint for section
    arcpy.management.FeatureVerticesToPoints(temp_section, "temp_midpoint", "MID")

    # find intersecting failure mechanisms
    score = "voldoende"
    scores = []
    for fm in failureMechanisms:
        # spatial join temp_section to fm
        arcpy.analysis.SpatialJoin(temp_section, fm, "temp_spatial_oordeel", "JOIN_ONE_TO_ONE", "KEEP_ALL", "", "CLOSEST", None, '')
        
        score = [cur[0] for cur in arcpy.da.SearchCursor("temp_spatial_oordeel", scorefield)][0]
        print (score, fm)	
        scores.append(score)


    if insufficientValue in scores:
        score = "onvoldoende"

    print (score)
    segmentRow[1] = score
    segmentCursor.updateRow(segmentRow)




arcpy.CopyFeatures_management("temp_trajectory_splitted", endCalcName)

    
