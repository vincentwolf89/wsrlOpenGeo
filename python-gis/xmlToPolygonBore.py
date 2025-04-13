from json.tool import main
from logging import getLogger
from xml.etree import ElementTree as ET, ElementInclude
import os
import arcpy


## aantekeningen:
# lagen met geotechnicalSoilName uitlezen!


arcpy.env.workspace = r'C:\Users\vince\Documents\ArcGIS\Projects\xml_boringen\xml_boringen.gdb'
gdb = r'C:\Users\vince\Documents\ArcGIS\Projects\xml_boringen\xml_boringen.gdb'
arcpy.env.overwriteOutput = True


xmlFiles = r'C:\Users\vince\Desktop\werk\Projecten\WSRL\xml_boringen_toevoegen\input\xml_hugo_jan_2023'
xyLayer = "xml_boringen_hugo_jan_2023"
routingLine = "basislijn_routing_totaal"


class xmlToPolygonBore(object):
    
    def __init__(self, xmlFiles,xyLayer,routingLine,gdb):
        self.xmlFiles = xmlFiles
        self.xyLayer = xyLayer
        self.routingLine = routingLine
        self.gdb = gdb

    
    def createFeatureclass(self, gdb, xyLayer):
        # maak nieuwe featureclass in gdb
        arcpy.CreateFeatureclass_management(gdb, xyLayer, "POINT", spatial_reference=28992)
        arcpy.AddField_management(xyLayer, 'testId', "TEXT")
        arcpy.AddField_management(xyLayer, 'operatorId', "DOUBLE", 2, field_is_nullable="NULLABLE")
        arcpy.AddField_management(xyLayer, 'startDate', "TEXT")
        arcpy.AddField_management(xyLayer, 'xLoc', "DOUBLE", 2, field_is_nullable="NULLABLE")
        arcpy.AddField_management(xyLayer, 'yLoc', "DOUBLE", 2, field_is_nullable="NULLABLE")
        arcpy.AddField_management(xyLayer, 'zLoc', "TEXT")
        arcpy.AddField_management(xyLayer, 'zLocMeasured', "DOUBLE", 2, field_is_nullable="NULLABLE")
        arcpy.AddField_management(xyLayer, 'ghg', "DOUBLE", 2, field_is_nullable="NULLABLE")
        arcpy.AddField_management(xyLayer, 'glg', "DOUBLE", 2, field_is_nullable="NULLABLE")
        arcpy.AddField_management(xyLayer, 'groundwaterLevel', "DOUBLE", 2, field_is_nullable="NULLABLE")
        arcpy.AddField_management(xyLayer, 'beginDepth', "DOUBLE", 2, field_is_nullable="NULLABLE")
        arcpy.AddField_management(xyLayer, 'endDepth', "DOUBLE", 2, field_is_nullable="NULLABLE")

        arcpy.AddField_management(xyLayer, 'upperBoundary', "DOUBLE", 2, field_is_nullable="NULLABLE")
        arcpy.AddField_management(xyLayer, 'upperBoundaryNAP', "DOUBLE", 2, field_is_nullable="NULLABLE")
        arcpy.AddField_management(xyLayer, 'lowerBoundary', "DOUBLE", 2, field_is_nullable="NULLABLE")
        arcpy.AddField_management(xyLayer, 'lowerBoundaryNAP', "DOUBLE", 2, field_is_nullable="NULLABLE")
        arcpy.AddField_management(xyLayer, 'anthropogenic', "TEXT")
        arcpy.AddField_management(xyLayer, 'geotechnicalSoilName', "TEXT")
        arcpy.AddField_management(xyLayer, 'tertiaryConstituent', "TEXT")
        arcpy.AddField_management(xyLayer, 'colour', "TEXT")

        arcpy.AddField_management(xyLayer, 'dispersedInhomogeneity', "TEXT")
        arcpy.AddField_management(xyLayer, 'organicMatterContentClass', "TEXT")
        arcpy.AddField_management(xyLayer, 'sandMedianClass', "TEXT")
        arcpy.AddField_management(xyLayer, 'sizeFraction', "TEXT")
        arcpy.AddField_management(xyLayer, 'angularity', "TEXT")
        arcpy.AddField_management(xyLayer, 'sphericity', "TEXT")

        print ("featureclass created for borepoints with xycoords")

        return xyLayer
  

    def readXmlBoreMain(self, xmlFile, xyLayer):



        tree = ET.parse(xmlFile)
        borehole_root = tree.getroot()
        ElementInclude.include(borehole_root)

        # borehole variables
        startDate = None
        testId = None
        xLoc = None
        yLoc = None
        zLoc = None
        zLocMeasured = None
        operatorId = None
        ghg = None
        glg = None
        groundwaterLevel = None
        beginDepth = None
        endDepth = None



        # find elements by iterating through the tree
        for elem in tree.iter():
            if "objectIdAccountableParty" in elem.tag:
                testId = elem.text

            if "meanHighestGroundwaterLevel" in elem.tag:
                ghg = float(elem.text)

            if "meanLowestGroundwaterLevel" in elem.tag:
                glg = float(elem.text)

            if "deliveredLocation" in elem.tag:
                for item in elem.iter():
                    if "pos" in item.tag:
                        xLoc = float(item.text.split(' ')[0])
                        yLoc = float(item.text.split(' ')[1])

            if "localVerticalReferencePoint" in elem.tag:
                zLoc = elem.text

        
            if "offset" in elem.tag:
                zLocMeasured = float(elem.text)
                readyForLayerIteration = True

            if "chamberOfCommerceNumber" in elem.tag:
                operatorId = float(elem.text)

            if "groundwaterLevel" in elem.tag:
                groundwaterLevel = float(elem.text)

            if "boringStartDate" in elem.tag:
                for item in elem:
                    startDate = item.text      

            if "finalDepthBoring" in elem.tag:
                endDepth = float(elem.text)

            if "boredInterval" in elem.tag:
                beginDepth = float(elem[0].text)

                     
     




        print ("xml file '{}' read and main variables read".format(xmlFile))
        returnValues = {
            'testId': testId,
            'operatorId':operatorId,
            'startDate': startDate,
            'ghg': ghg,
            'glg':glg,
            'groundwaterLevel':groundwaterLevel,
            'beginDepth': beginDepth,
            'endDepth':endDepth,
            'zLoc': zLoc,
            'zLocMeasured': zLocMeasured,
            'xLoc': xLoc,
            'yLoc': yLoc
        }

        return returnValues
        

    def readXmlBoreLayer(self, xmlFile, xyLayer,mainValues):
        cursor = arcpy.da.InsertCursor(xyLayer, ['testId', 'operatorId', 'startDate','xLoc', 'yLoc', 'zLoc', 'zLocMeasured', 'ghg', 'glg', 'groundwaterLevel','beginDepth',
        'endDepth','upperBoundary', 'upperboundaryNAP', 'lowerBoundary','lowerBoundaryNAP','anthropogenic', 'geotechnicalSoilName', 'tertiaryConstituent', 'colour','dispersedInhomogeneity','organicMatterContentClass','sandMedianClass','sizeFraction','angularity','sphericity', 'SHAPE@XY'])




        tree = ET.parse(xmlFile)
        borehole_root = tree.getroot()
        ElementInclude.include(borehole_root)

        # borehole variables
        startDate = mainValues['startDate']
        operatorId = mainValues['operatorId']
        testId = mainValues['testId']
        ghg = mainValues['ghg']
        glg = mainValues['glg']
        groundwaterLevel = mainValues['groundwaterLevel']
        beginDepth = mainValues['beginDepth']
        endDepth = mainValues['endDepth']
        zLoc = mainValues['zLoc']

        xLoc = mainValues['xLoc']
        yLoc = mainValues['yLoc']



        zLocMeasured = mainValues['zLocMeasured']
        upperBoundary = None
        upperBoundaryNAP = None
        lowerBoundary = None
        lowerBoundaryNAP = None
        anthropogenic = None
        geotechnicalSoilName = None
        tertiaryConstituent = None
        colour = None
        dispersedInhomogeneity = None
        organicMatterContentClass = None
        sandMedianClass = None
        sizeFraction = None
        angularity = None
        sphericity = None





        # find elements by iterating through the tree
        for elem in tree.iter():
            if "descriptiveBoreholeLog" in elem.tag:
                for item in elem:
                    if "layer" in item.tag:
                        for layeritem in item:
                       

                            if ("upperBoundary" in layeritem.tag and "Determination" not in layeritem.tag):
                                upperBoundary = float(layeritem.text)
                                upperBoundaryNAP = zLocMeasured - upperBoundary
                     

                            if ("lowerBoundary" in layeritem.tag and "Determination" not in layeritem.tag):
                                lowerBoundary = float(layeritem.text)
                                lowerBoundaryNAP = zLocMeasured - lowerBoundary
                       
                            if "anthropogenic" in layeritem.tag:
                                anthropogenic = layeritem.text
                             
                    
              
                            if "soil" in layeritem.tag:
                                for soilitem in layeritem:
                                    if "geotechnicalSoilName" in soilitem.tag:
                                        geotechnicalSoilName = soilitem.text
                                    if "tertiaryConstituent" in soilitem.tag:
                                        tertiaryConstituent = soilitem.text
                                    if "colour" in soilitem.tag:
                                        colour = soilitem.text
                                    if "dispersedInhomogeneity" in soilitem.tag:
                                        dispersedInhomogeneity = soilitem.text
                                    if "organicMatterContentClass" in soilitem.tag:
                                        organicMatterContentClass = soilitem.text
                                    if "sandMedianClass" in soilitem.tag:
                                        sandMedianClass = soilitem.text

                                    if "grainshape" in soilitem.tag:
                                        for sanditem in soilitem:
                                            if "sizeFraction" in sanditem.tag:
                                                sizeFraction = sanditem.text
                                            if "angularity" in sanditem.tag:
                                                angularity = sanditem.text
                                            if "sphericity" in sanditem.tag:
                                                sphericity = sanditem.text



        
        

                        # write new row to featureclass

                        insertRow = (testId, operatorId, startDate, xLoc, yLoc, zLoc, zLocMeasured, ghg, glg, groundwaterLevel, beginDepth, endDepth, 
                        upperBoundary, upperBoundaryNAP, lowerBoundary,lowerBoundaryNAP, anthropogenic, geotechnicalSoilName, tertiaryConstituent, 
                        colour, dispersedInhomogeneity,organicMatterContentClass,sandMedianClass, sizeFraction, angularity, sphericity, (xLoc,yLoc))
                                                                                               
                        cursor.insertRow(insertRow)
           



        print ("xml file '{}' written to featureclass".format(xmlFile))
    def createBoreShapes(self, xyLayer, routingLine):


        ## module polyline
        # sources
        borePoints = xyLayer
        boringlagen = "T_boringlaag" # templayer
        targetBoringen = 'L_LP_boringen' # lines to create

        #variables for plotting
        OffsetBIT = 300
        OffsetBUT = 300

        #locate borepoints
        arcpy.LocateFeaturesAlongRoutes_lr(borePoints, routingLine, "rid", "200 Meters", boringlagen, "RID POINT MEAS", "FIRST", "DISTANCE", "ZERO", "FIELDS", "M_DIRECTON")

        # fields to edit
        fieldsBoringen = ['testId','geotechnicalSoilName','lTop','lBot','MEAS','RID']



        # create fields in table
        arcpy.AddField_management(boringlagen,"lTop","DOUBLE")
        arcpy.AddField_management(boringlagen,"lBot","DOUBLE")
        arcpy.AddField_management(boringlagen,"lMid","DOUBLE")


        updateFields = ["upperBoundaryNAP","lowerBoundaryNAP","upperBoundaryNAP","geotechnicalSoilName","lTop","lBot","lMid","geotechnicalSoilName","Distance"]


        # set values for fields
        with arcpy.da.UpdateCursor(boringlagen,updateFields) as Ucur:
            for row in Ucur:
                if row[8] < 10 and row[8] > -5:
                    row[4] = row[0] * 10
                    row[5] = row[1] * 10
                    row[6] = row[2] * 10
                    row[7] = row[3]
                
                    Ucur.updateRow(row)

                if row[8] < -5:
                    row[4] = row[0] * 10 - OffsetBIT
                    row[5] = row[1] * 10 - OffsetBIT
                    row[6] = row[2] * 10 - OffsetBIT
                    row[7] = row[3]
        
                    Ucur.updateRow(row)

                if row[8] > 10:
                    row[4] = row[0] * 10 + OffsetBUT
                    row[5] = row[1] * 10 + OffsetBUT
                    row[6] = row[2] * 10 + OffsetBUT
                    row[7] = row[3]
            
                    Ucur.updateRow(row)

        del Ucur

    

        # create LLP Boringen
        arcpy.CreateFeatureclass_management(gdb, targetBoringen, "POLYLINE", spatial_reference=28992)
        arcpy.AddField_management(targetBoringen, 'testId', "TEXT")
        arcpy.AddField_management(targetBoringen, 'geotechnicalSoilName', "TEXT")
        arcpy.AddField_management(targetBoringen, 'RID', "TEXT")




        # verwerken gegevens boringen uit tabel naar lijnenfeature
        with arcpy.da.SearchCursor(boringlagen,fieldsBoringen) as Scur: # uitlezen tabel
            for row in Scur:
                lTop = row[2]
                lBot = row[3]
                RID = row[5]
                testId = row[0]
                geotechnicalSoilName = row[1]
                if geotechnicalSoilName == "":
                    geotechnicalSoilName == "NTB"
                else:
                    geotechnicalSoilName = geotechnicalSoilName
                MEAS = row[4]
                coordList = [(MEAS, lTop),(MEAS,lBot)]
                with arcpy.da.InsertCursor(targetBoringen,['SHAPE@','testId','geotechnicalSoilName','RID']) as Icur: #wegschrijven geometrie met gegevens
                    
                    Icur.insertRow([coordList,testId,geotechnicalSoilName,RID])
                del Icur

        del Scur

        # remove tempfiles
        arcpy.Delete_management(boringlagen)

        ## module polygon

        # sources
        boringLijn = "L_LP_boringen"


        # output

        boringPolygon = "PG_LP_boringen"

        arcpy.CreateFeatureclass_management(gdb, boringPolygon, "POLYGON", spatial_reference=28992)
        arcpy.AddField_management(boringPolygon, 'testId', "TEXT")
        arcpy.AddField_management(boringPolygon, 'geotechnicalSoilName', "TEXT")
        arcpy.AddField_management(boringPolygon, 'RID', "TEXT")


        # fields
        boringFields = ["SHAPE@","testId","geotechnicalSoilName","RID"]
        inputFields = ["SHAPE@","testId","geotechnicalSoilName","RID"]


        verbFactor = 1

        pointList = []

        with arcpy.da.SearchCursor(boringLijn, boringFields) as Scur:
            for row in Scur:
                boreHole = row[1]
                geotechnicalSoilName = row[2]
                RID = row[3]
                
                for part in row[0]:
                    for point in part:
                        pointList.append(point.X)
                        pointList.append(point.Y)
                

                xStartUpper = pointList[0] - 5 * verbFactor
                xEndUpper = xStartUpper + (10)*verbFactor
                yTopLower = pointList[1]
                yBotLower = pointList[3]
                
                with arcpy.da.InsertCursor(boringPolygon,inputFields) as Icur:
                    borePolygon = arcpy.Polygon(arcpy.Array([arcpy.Point(xStartUpper,yTopLower),arcpy.Point(xEndUpper,yTopLower),arcpy.Point(xEndUpper,yBotLower),arcpy.Point(xStartUpper,yBotLower),arcpy.Point(xStartUpper,yTopLower)]))
                    Icur.insertRow([borePolygon,boreHole,geotechnicalSoilName,RID])


                del Icur



                pointList = []
          




        del Scur

        print ("bore-shapes written...")


    def execute(self):
        self.createFeatureclass(self.gdb,self.xyLayer)
        for xmlFile in os.listdir(self.xmlFiles):
            xmlFile = os.path.join(self.xmlFiles, xmlFile)
            mainValues = self.readXmlBoreMain(xmlFile,self.xyLayer)
            self.readXmlBoreLayer(xmlFile,self.xyLayer,mainValues)
           

          

        self.createBoreShapes(self.xyLayer,self.routingLine)


xmlBore = xmlToPolygonBore(xmlFiles,xyLayer,routingLine,gdb)
xmlBore.execute()

 