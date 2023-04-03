
import arcpy
from arcpy.sa import *
from itertools import groupby
import numpy as np
import pandas as pd

arcpy.CheckOutExtension("Spatial")
sr = arcpy.SpatialReference(28992)
import numpy as np
arcpy.env.workspace = r"C:\Users\vince\Documents\ArcGIS\Projects\waterlopen safe maart 2023\werkdata.gdb"
arcpy.env.overwriteOutput = True

outputRasters = "C:/Users/vince/Documents/ArcGIS/Projects/waterlopen safe maart 2023/output.gdb/"
leggerData = r"C:\Users\vince\Documents\ArcGIS\Projects\waterlopen safe maart 2023\waterlopen safe maart 2023.gdb\waterlopen_safe_binnen_200m"

boezemNormal = r"C:\Users\vince\Documents\ArcGIS\Projects\waterlopen safe maart 2023\waterlopen safe maart 2023.gdb\bgt_waterlopen_safe_binnen_200m"
boezemBuffers = r"C:\Users\vince\Documents\ArcGIS\Projects\waterlopen safe maart 2023\waterlopen safe maart 2023.gdb\bgt_waterlopen_safe_binnen_200m_1mbuffer_testsectie"
# # measurementsCrossSections = r"D:\GoogleDrive\HDSR\hdsr_waterlopen\rwk_clean.gdb\rwk_watergangen_wit_2022"
# measurementsCrossSections = r"C:\Users\vince\Desktop\hdsr_2022\waterlopen\hdsr_waterlopen\rwk_clean.gdb\dummy"
ahn4Total = r"C:\Users\vince\Documents\ArcGIS\Projects\safe ahn\safe ahn.gdb\safe_ahn4_200mbuffer"

##input

# measurements
elevationFieldMeasurements = "vast_hoog"

defaultOffset = 1 # offset in m for bgt waterlopen input
sectionName = 'code'
taludField = 'talud'
bodemField = 'bodem'
insteekField = 'insteek'
defaultInsteekField = "defaultInsteek"

# these need to be implemented in case of nodata
defaultTalud = 1.5 
defaultBodemOffset = 1.5

joinTolerance = 0.1
lineSteps = 0.2
measureMentSearchDistance = 0


def getnums(s, e,i):
   return (np.arange(s, e, i))

def average(lijst):
    return sum(lijst) / len(lijst)

intervals = getnums(-lineSteps,-10,-lineSteps)

def fillLegger():
    # iterate over leggerlines
    leggerCursor = arcpy.da.UpdateCursor(leggerData,["SHAPE@",insteekField,defaultInsteekField])

    count = 0
    for lRow in leggerCursor:

        count += 1
       
        leggerLine = lRow[0]
        buffer = arcpy.analysis.Buffer(leggerLine, "temp_buffer_legger", 50, "FULL","ROUND")
        bufferClip = arcpy.analysis.Clip(boezemNormal, buffer, "temp_buffer_boezem_clip", None)
        bufferLine= arcpy.PolygonToLine_management(bufferClip, "buffer_boezem_clip_line")
        try:
            bufferPoints = arcpy.management.GeneratePointsAlongLines(bufferLine, "temp_boezem_buffer_points", "PERCENTAGE", None, 10, None)
            bufferPointsZ = arcpy.sa.ExtractValuesToPoints(bufferPoints, ahn4Total, "temp_boezem_buffer_points_z", "INTERPOLATE", "VALUE_ONLY")
            zValues = []
            avCursor = arcpy.da.SearchCursor(bufferPointsZ,"RASTERVALU")
            for avRow in avCursor:
                if avRow[0] is not None:
                    zValues.append(avRow[0])
            
            if zValues:
                averageZ = average(zValues)
                print ("Average z-value for this watersection is: {}".format(averageZ))
                lRow[2] = averageZ
                leggerCursor.updateRow(lRow)
            else:
                print ("No suitable z-values have been found...")
        except Exception as e:
            print ("no suitable polygon for clipping found")



        print (count)


    
def makeGrids():
    boezemCursor = arcpy.da.SearchCursor(boezemBuffers,["SHAPE@","mainAngle","OID@"])

    for row in boezemCursor:
  
        # if row[2] > 74:
        clippingMask = arcpy.CopyFeatures_management(row[0], "clippingMask")
        mainAngle = row[1]-90
        bufferList = []
        index = 0 
        for interval in intervals:
        
            try:
                buffer = arcpy.analysis.Buffer(row[0], "buffer_{}".format(index), interval, "FULL","ROUND")
                buffer_line = arcpy.PolygonToLine_management(buffer, "buffer_line_{}".format(index))
                arcpy.AddField_management(buffer_line, "interval","DOUBLE", 2, field_is_nullable="NULLABLE")
                arcpy.CalculateField_management(buffer_line, "interval", index, "PYTHON")
                bufferList.append(buffer_line)
                index += 1
            except Exception as e:
                pass

            
        buffers = arcpy.management.Merge(bufferList, "buffers_line", "", "ADD_SOURCE_INFO")
        rasterPointList = []
        # subdivide into workable areas
        subsectionName = "subsections_{}".format(str(row[2]))
        subsectionRasterName = "subsections_{}_raster".format(str(row[2]))
        
        try:
            arcpy.management.SubdividePolygon(row[0], "subsections_multipart", "EQUAL_AREAS", None, "3000 SquareMeters", None, mainAngle, "STRIPS")
            arcpy.management.MultipartToSinglepart("subsections_multipart", subsectionName)
        except Exception as e:
            arcpy.CopyFeatures_management(row[0], subsectionName)

        

        subSectionCursor = arcpy.da.SearchCursor(subsectionName,["SHAPE@"])

        sectionIndex = 0
        for subRow in subSectionCursor:

            # get centerpoint of polygon for best fit with leggerdata
            arcpy.management.FeatureToPoint(subRow[0], "temp_centerpoint", "INSIDE")
            arcpy.analysis.SpatialJoin("temp_centerpoint", leggerData, "temp_centerpoint_leggerdata", "JOIN_ONE_TO_ONE", "KEEP_ALL", "", "CLOSEST", None, '')
            subSection = arcpy.analysis.SpatialJoin(subRow[0], "temp_centerpoint_leggerdata", "subSection", "JOIN_ONE_TO_ONE", "KEEP_ALL", "", "INTERSECT", None, '')

            # arcpy.MakeFeatureLayer_management(leggerData, "templayer") 
            # arcpy.management.SelectLayerByLocation("templayer", "INTERSECT", subRow[0], "", "NEW_SELECTION", "NOT_INVERT")
            # arcpy.CopyFeatures_management("templayer", "tempLeggerIsects")

            
            # sortedIsects = arcpy.Sort_management("tempLeggerIsects", "tempLeggerIsects_sorted", [["Shape_Length", "DESCENDING"]])

            # print ("Subsection connected with leggerdata, going on...")
            # # remove shorter ones
            # highestOID = int([f[0] for f in arcpy.da.SearchCursor(sortedIsects, 'OID@')][0])
            # isectCursor = arcpy.da.UpdateCursor(sortedIsects, "OID@")
            # for iRow in isectCursor:
            #     if int(iRow[0]) == highestOID:
            #         pass
            #     else:
            #         isectCursor.deleteRow()
            # del isectCursor, iRow
            
                        
            # subSection = arcpy.analysis.SpatialJoin(subRow[0], "tempLeggerIsects_sorted", "subSection", "JOIN_ONE_TO_ONE", "KEEP_ALL", "", "INTERSECT", None, '')
            # sectionName = [f[0] for f in arcpy.da.SearchCursor("subSection", 'CODE')][0]
            
            taludValue = [f[0] for f in arcpy.da.SearchCursor("subSection", taludField)][0]
            bodemValue = [f[0] for f in arcpy.da.SearchCursor("subSection", bodemField)][0]
            insteekValue = [f[0] for f in arcpy.da.SearchCursor("subSection", insteekField)][0]


            # clip bufferlines for subsection
            arcpy.analysis.Clip("buffers_line", subSection, "buffers_subsection", None)

            # add default measurements, in case needed
            arcpy.AddField_management("buffers_subsection", "defaultZ","DOUBLE", 2, field_is_nullable="NULLABLE")
            arcpy.AddField_management("buffers_subsection", "meanZ","DOUBLE", 2, field_is_nullable="NULLABLE")
            arcpy.Sort_management("buffers_subsection", "buffers_subsection_sorted", [["interval", "ASCENDING"]])

            defaultInsteekValue = False
            # check for missing values, if so do work
            if taludValue == None:
                taludValue = defaultTalud

            
            if insteekValue == None:
                insteekValue = [f[0] for f in arcpy.da.SearchCursor("subSection", defaultInsteekField)][0]
                defaultInsteekValue = True
                print ("Insteek value using default: {}".format(insteekValue))
            else:
                print ("Insteek value found, using: {}".format(insteekValue))


            bodemValue = insteekValue - defaultBodemOffset
            defaultZcursor = arcpy.da.UpdateCursor("buffers_subsection_sorted",["interval","defaultZ"])

            bufferSize = 0
            value = insteekValue
            for dRow in defaultZcursor:
                if bufferSize < defaultOffset: 
                    dRow[1] = value
                    bufferSize += lineSteps
                    # value -= (taludValue*lineSteps)

                elif bufferSize == defaultOffset:
                    dRow[1] = value
                    value -= (taludValue*lineSteps)/2
                    bufferSize += lineSteps

                elif bufferSize > defaultOffset and value > bodemValue:
                    dRow[1] = value
                    value -= (taludValue*lineSteps)/2
                    bufferSize += lineSteps
                elif bufferSize > 0 and value <= bodemValue:
                    dRow[1] = bodemValue
                
                defaultZcursor.updateRow(dRow)


            del defaultZcursor
        

            arcpy.CalculateField_management("buffers_subsection_sorted", "meanZ", "!defaultZ!", "PYTHON3")
            rasterpoints = arcpy.management.GeneratePointsAlongLines("buffers_subsection_sorted", "rasterpoints_{}".format(sectionIndex), "DISTANCE", "1 Meters", None, None)
            rasterPointList.append(rasterpoints)


            sectionIndex +=1
            print(sectionIndex)

        

            

            

        

        try:
            rasterpointsTotal= arcpy.management.Merge(rasterPointList, "rasterpointsTotal_", "", "ADD_SOURCE_INFO")
            arcpy.ddd.Idw(rasterpointsTotal, "meanZ", "tempraster", 0.5, 2, "VARIABLE 8", None)
            
            # clip raster on subsection

            clippingExtent = arcpy.Describe(clippingMask)
            xmin = clippingExtent.extent.XMin
            xmax = clippingExtent.extent.XMax
            ymin = clippingExtent.extent.YMin
            ymax = clippingExtent.extent.YMax

            clippingExtent = "{} {} {} {}".format(xmin,ymin,xmax,ymax)


            arcpy.management.Clip("tempraster", clippingExtent, outputRasters+subsectionRasterName, clippingMask, "3,4e+38", "ClippingGeometry", "MAINTAIN_EXTENT")
            print("raster written: {}".format(row[2]))


        except:
            pass

# fillLegger()
makeGrids()




