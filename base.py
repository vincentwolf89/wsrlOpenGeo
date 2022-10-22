import arcpy
import math
import pandas as pd
arcpy.env.overwriteOutput = True

def CopyParallelL(plyP,sLength): #functie voor profielen maken haaks op trajectlijn
    part=plyP.getPart(0)
    lArray=arcpy.Array()
    for ptX in part:
        dL=plyP.measureOnLine(ptX)
        ptX0=plyP.positionAlongLine (dL-0.01).firstPoint
        ptX1=plyP.positionAlongLine (dL+0.01).firstPoint
        dX=float(ptX1.X)-float(ptX0.X)
        dY=float(ptX1.Y)-float(ptX0.Y)
        lenV=math.hypot(dX,dY)
        sX=-dY*sLength/lenV;sY=dX*sLength/lenV
        leftP=arcpy.Point(ptX.X+sX,ptX.Y+sY)
        lArray.add(leftP)
    array = arcpy.Array([lArray])
    section=arcpy.Polyline(array)
    return section

def CopyParallelR(plyP,sLength): #functie voor profielen maken haaks op trajectlijn
    part=plyP.getPart(0)
    rArray=arcpy.Array()
    for ptX in part:
        dL=plyP.measureOnLine(ptX)
        ptX0=plyP.positionAlongLine (dL-0.01).firstPoint
        ptX1=plyP.positionAlongLine (dL+0.01).firstPoint
        dX=float(ptX1.X)-float(ptX0.X)
        dY=float(ptX1.Y)-float(ptX0.Y)
        lenV=math.hypot(dX,dY)
        sX=-dY*sLength/lenV;sY=dX*sLength/lenV
        rightP=arcpy.Point(ptX.X-sX, ptX.Y-sY)
        rArray.add(rightP)
    array = arcpy.Array([rArray])
    section=arcpy.Polyline(array)
    return section

def excelWriterTraject(uitvoerpunten,excel, veldnamen):
    # df van profielpunten
    array = arcpy.da.FeatureClassToNumPyArray(uitvoerpunten, veldnamen)
    df = pd.DataFrame(array)

    #export excel
    df.to_excel(excel)  

    print ("Excel gemaakt van profieldata")


def copy_trajectory_lr(trajectlijn,code,afstand):
    existing_fields = arcpy.ListFields(trajectlijn)
    needed_fields = ['OBJECTID','OBJECTID_1','Shape','Shape_Length','SHAPE', 'SHAPE_Length',code]
    for field in existing_fields:
        if field.name not in needed_fields:
            arcpy.DeleteField_management(trajectlijn, field.name)

    arcpy.AddField_management(trajectlijn, "Width", "DOUBLE", 2, field_is_nullable="NULLABLE")
    arcpy.CalculateField_management(trajectlijn, "Width", afstand, "PYTHON")

    arcpy.management.CopyFeatures(trajectlijn, "river")
    arcpy.management.CopyFeatures(trajectlijn, "land")
    land = "land"
    river = "river"


    with arcpy.da.UpdateCursor(land, ("Shape@", "Width")) as cursor:
        for shp, w in cursor:
            LeftLine = CopyParallelL(shp, w)
            cursor.updateRow((LeftLine, w))

    with arcpy.da.UpdateCursor(river, ("Shape@", "Width")) as cursor:
        for shp, w in cursor:
            RightLine = CopyParallelR(shp, w)
            cursor.updateRow((RightLine, w))

    print ('Trajectlijnen-offset gemaakt')


def generate_profiles(profiel_interval,profiel_lengte_land,profiel_lengte_rivier,trajectlijn,code,profielen):
    # traject to points
    arcpy.GeneratePointsAlongLines_management(trajectlijn, 'traject_punten', 'DISTANCE', Distance=profiel_interval, Include_End_Points='NO_END_POINTS')
    arcpy.AddField_management('traject_punten', "profielnummer", "DOUBLE", 2, field_is_nullable="NULLABLE")
    arcpy.AddField_management('traject_punten', "lengte_landzijde", "DOUBLE", 2, field_is_nullable="NULLABLE")
    arcpy.AddField_management('traject_punten', "lengte_rivierzijde", "DOUBLE", 2, field_is_nullable="NULLABLE")
    arcpy.CalculateField_management('traject_punten', "profielnummer", '!OBJECTID!', "PYTHON")
    arcpy.CalculateField_management('traject_punten', "lengte_landzijde", profiel_lengte_land, "PYTHON")
    arcpy.CalculateField_management('traject_punten', "lengte_rivierzijde", profiel_lengte_rivier, "PYTHON")

    # route voor trajectlijn
    # arcpy.CreateRoutes_lr(trajectlijn, code, "route_traject", "LENGTH", "", "", "UPPER_LEFT", "1", "0", "IGNORE", "INDEX")

    existing_fields = arcpy.ListFields(trajectlijn)
    needed_fields = ['OBJECTID','OBJECTID_1', 'SHAPE', 'SHAPE_Length','Shape','Shape_Length',code]
    for field in existing_fields:
        if field.name not in needed_fields:
            arcpy.DeleteField_management(trajectlijn, field.name)
    arcpy.AddField_management(trajectlijn, "van", "DOUBLE", 2, field_is_nullable="NULLABLE")
    arcpy.AddField_management(trajectlijn, "tot", "DOUBLE", 2, field_is_nullable="NULLABLE")
    arcpy.CalculateField_management(trajectlijn, "van", 0, "PYTHON")
    # arcpy.CalculateField_management(trajectlijn, "tot", "!Shape_Length!", "PYTHON")
    arcpy.CalculateField_management(trajectlijn, "tot", "round(!shape.length!)", "PYTHON")
    arcpy.CreateRoutes_lr(trajectlijn, code, 'route_traject', "TWO_FIELDS", "van", "tot", "", "1",
                          "0", "IGNORE", "INDEX")


    # locate profielpunten
    arcpy.LocateFeaturesAlongRoutes_lr('traject_punten', 'route_traject', code, "1.5 Meters", 'tabel_traject_punten',
                                       "RID POINT MEAS", "FIRST", "DISTANCE", "ZERO", "FIELDS",
                                       "M_DIRECTON")

    # offset rivierdeel profiel
    arcpy.MakeRouteEventLayer_lr('route_traject', code, 'tabel_traject_punten', "rid POINT meas", 'deel_rivier',
                                 "lengte_rivierzijde", "NO_ERROR_FIELD", "NO_ANGLE_FIELD", "NORMAL", "ANGLE", "RIGHT",
                                 "POINT")

    arcpy.MakeRouteEventLayer_lr('route_traject', code, 'tabel_traject_punten', "rid POINT meas", 'deel_land',
                                 "lengte_landzijde", "NO_ERROR_FIELD", "NO_ANGLE_FIELD", "NORMAL", "ANGLE", "LEFT",
                                 "POINT")
    # temp inzicht layer
    arcpy.management.CopyFeatures('deel_rivier', "temp_rivierdeel")
    arcpy.management.CopyFeatures('deel_land', "temp_landdeel")
    arcpy.AddField_management('temp_rivierdeel', "id", "DOUBLE", 2, field_is_nullable="NULLABLE")
    arcpy.AddField_management('temp_landdeel', "id", "DOUBLE", 2, field_is_nullable="NULLABLE")
    arcpy.CalculateField_management('temp_rivierdeel', "id", 2, "PYTHON")
    arcpy.CalculateField_management('temp_landdeel', "id", 1, "PYTHON")

    arcpy.Merge_management("'temp_rivierdeel';'temp_landdeel'", 'merge_profielpunten')
    arcpy.PointsToLine_management('merge_profielpunten', profielen, "profielnummer", "id", "NO_CLOSE")

    arcpy.SpatialJoin_analysis(profielen, trajectlijn, 'profielen_temp', "JOIN_ONE_TO_ONE", "KEEP_ALL", match_option="INTERSECT")
    arcpy.management.CopyFeatures('profielen_temp', profielen)
    # arcpy.FlipLine_edit(profielen)

    print ('Profielen gemaakt op trajectlijn')

def set_measurements_trajectory(profielen,trajectlijn,code,stapgrootte_punten): #rechts = rivier, profielen van binnen naar buiten
    # clean feature
    existing_fields = arcpy.ListFields(profielen)
    delete_fields = ['van','tot']
    for field in existing_fields:
        if field.name in delete_fields:
            arcpy.DeleteField_management(profielen, field.name)

    # add needed fields
    #arcpy.AddField_management(profielen, "profielnummer", "DOUBLE", 2, field_is_nullable="NULLABLE")
    arcpy.AddField_management(profielen, "van", "DOUBLE", 2, field_is_nullable="NULLABLE")
    arcpy.AddField_management(profielen, "tot", "DOUBLE", 2, field_is_nullable="NULLABLE")

    #arcpy.CalculateField_management(profielen, "profielnummer", '!OBJECTID!', "PYTHON")

    # split profiles
    rivierlijn = "river"
    landlijn = "land"
    clusterTolerance = 1
    invoer = [profielen, trajectlijn]
    uitvoer = 'snijpunten_centerline'
    arcpy.Intersect_analysis(invoer, uitvoer, "", clusterTolerance, "point")
    arcpy.SplitLineAtPoint_management(profielen, uitvoer, 'profielsplits', 1)

    velden = ['profielnummer', 'van', 'tot',code]

    fieldmappings = arcpy.FieldMappings()
    fieldmappings.addTable('profielsplits')
    fieldmappings.addTable(rivierlijn)
    fieldmappings.addTable(landlijn)
    keepers = velden

    # join splits to river/land parts
    for field in fieldmappings.fields:
        if field.name not in keepers:
            fieldmappings.removeFieldMap(fieldmappings.findFieldMapIndex(field.name))

    arcpy.SpatialJoin_analysis('profielsplits', rivierlijn, 'profieldeel_rivier', "JOIN_ONE_TO_ONE", "KEEP_COMMON", fieldmappings,
                               match_option="INTERSECT")
    arcpy.SpatialJoin_analysis('profielsplits', landlijn, 'profieldeel_land', "JOIN_ONE_TO_ONE", "KEEP_COMMON",
                               fieldmappings,
                               match_option="INTERSECT")

    # create routes
    arcpy.CalculateField_management("profieldeel_rivier", "tot", '!Shape_Length!', "PYTHON")
    arcpy.CalculateField_management("profieldeel_land", "tot", '!Shape_Length!', "PYTHON")
    arcpy.CalculateField_management("profieldeel_rivier", "van", 0, "PYTHON")
    arcpy.CalculateField_management("profieldeel_land", "van", 0, "PYTHON")


    arcpy.CreateRoutes_lr('profieldeel_rivier', "profielnummer", "routes_rivier_", "TWO_FIELDS", "van", "tot", "", "1", "0",
                          "IGNORE", "INDEX")

    arcpy.CreateRoutes_lr('profieldeel_land', "profielnummer", "routes_land_", "TWO_FIELDS", "tot", "van", "", "1",
                          "0", "IGNORE", "INDEX")

    #join code
    velden = ['profielnummer',code]
    fieldmappings = arcpy.FieldMappings()
    fieldmappings.addTable('routes_land_')
    fieldmappings.addTable('routes_rivier_')
    fieldmappings.addTable(trajectlijn)

    keepers = velden
    for field in fieldmappings.fields:
        if field.name not in keepers:
            fieldmappings.removeFieldMap(fieldmappings.findFieldMapIndex(field.name))

    arcpy.SpatialJoin_analysis('routes_rivier_', trajectlijn, 'routes_rivier', "JOIN_ONE_TO_ONE", "KEEP_COMMON", match_option="INTERSECT",search_radius=1)
    arcpy.SpatialJoin_analysis('routes_land_', trajectlijn, 'routes_land', "JOIN_ONE_TO_ONE", "KEEP_COMMON", match_option="INTERSECT",search_radius=1)

    # generate points
    arcpy.GeneratePointsAlongLines_management('routes_land', 'punten_land', 'DISTANCE', Distance= stapgrootte_punten)
    arcpy.GeneratePointsAlongLines_management('routes_rivier', 'punten_rivier', 'DISTANCE', Distance=stapgrootte_punten)


    # id field for joining table
    arcpy.AddField_management('punten_land', 'punt_id', "DOUBLE", field_precision=2, field_is_nullable="NULLABLE")
    arcpy.AddField_management('punten_rivier', 'punt_id', "DOUBLE", field_precision=2, field_is_nullable="NULLABLE")
    arcpy.CalculateField_management("punten_land", "punt_id", '!OBJECTID!', "PYTHON")
    arcpy.CalculateField_management("punten_rivier", "punt_id", '!OBJECTID!', "PYTHON")


    # find points along routes
    Output_Event_Table_Properties = "RID POINT MEAS"
    arcpy.LocateFeaturesAlongRoutes_lr('punten_land', 'routes_land', "profielnummer", "1 Meters",
                                       'uitvoer_tabel_land', Output_Event_Table_Properties, "FIRST", "DISTANCE", "ZERO",
                                       "FIELDS", "M_DIRECTON")
    arcpy.LocateFeaturesAlongRoutes_lr('punten_rivier', 'routes_rivier', "profielnummer", "1 Meters",
                                       'uitvoer_tabel_rivier', Output_Event_Table_Properties, "FIRST", "DISTANCE", "ZERO",
                                       "FIELDS", "M_DIRECTON")

    # join fields from table
    arcpy.JoinField_management('punten_land', 'punt_id', 'uitvoer_tabel_land', 'punt_id', 'MEAS')
    arcpy.JoinField_management('punten_rivier', 'punt_id', 'uitvoer_tabel_rivier', 'punt_id', 'MEAS')
    arcpy.AlterField_management('punten_land', 'MEAS', 'afstand',clear_field_alias="CLEAR_ALIAS")
    arcpy.AlterField_management('punten_rivier', 'MEAS', 'afstand',clear_field_alias="CLEAR_ALIAS")

    with arcpy.da.UpdateCursor('punten_rivier', ['profielnummer', 'afstand']) as cursor:
        for row in cursor:
            row[1] = row[1]*-1
            cursor.updateRow(row)

    # fieldmappings = arcpy.FieldMappings()
    # fieldmappings.addTable('punten_land')
    # fieldmappings.addTable('punten_rivier')
    # fieldmappings.addTable('snijpunten_centerline')

    # velden = ['profielnummer', 'afstand', code]
    # keepers = velden

    # for field in fieldmappings.fields:
    #     if field.name not in keepers:
    #         fieldmappings.removeFieldMap(fieldmappings.findFieldMapIndex(field.name))

    arcpy.FeatureToPoint_management("snijpunten_centerline", "punten_centerline")
    arcpy.management.Merge(['punten_land', 'punten_rivier','punten_centerline'], 'punten_profielen')

    arcpy.management.CalculateField("punten_profielen", "afstand", 'round(!afstand!, 1)', "PYTHON3")

    # set centerline values to 0
    with arcpy.da.UpdateCursor('punten_profielen', ['afstand']) as cursor:
        for row in cursor:
            if row[0] == None:
                row[0] = 0
                cursor.updateRow(row)

    print ('Meetpunten op routes gelokaliseerd')

def extract_z_arcpy(invoerpunten, uitvoerpunten, raster): #

    # Test de ArcGIS Spatial Analyst extension license
    arcpy.CheckOutExtension("Spatial")

    # Koppel z-waardes
    arcpy.sa.ExtractValuesToPoints(invoerpunten, raster, uitvoerpunten, "NONE", "VALUE_ONLY")

    # Pas het veld 'RASTERVALU' aan naar 'z_ahn'
    arcpy.AlterField_management(uitvoerpunten, 'RASTERVALU', 'z_ahn')
    print ('Hoogtewaarde aan punten gekoppeld')

def add_xy(uitvoerpunten,code,trajectlijn):

    # existing_fields = arcpy.ListFields(uitvoerpunten)
    # needed_fields = ['OBJECTID','OBJECTID_1','OID@' 'Shape', 'profielnummer', 'afstand', 'z_ahn', code]
    # # for field in existing_fields:
    #     if field.name not in needed_fields:
    #         arcpy.DeleteField_management(trajectlijn, field.name)

    arcpy.env.outputCoordinateSystem = arcpy.Describe(uitvoerpunten).spatialReference
    # Set local variables
    in_features = uitvoerpunten
    properties = "POINT_X_Y_Z_M"
    length_unit = ""
    area_unit = ""
    coordinate_system = ""

    # Generate the extent coordinates using Add Geometry Properties tool
    arcpy.AddGeometryAttributes_management(in_features, properties, length_unit,
                                           area_unit,
                                           coordinate_system)

    arcpy.AlterField_management(uitvoerpunten, 'POINT_X', 'x')
    arcpy.AlterField_management(uitvoerpunten, 'POINT_Y', 'y')

    print ('XY-coordinaten aan punten gekoppeld')
