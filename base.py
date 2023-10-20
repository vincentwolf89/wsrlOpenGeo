import arcpy
import math
import pandas as pd
from xlsxwriter.workbook import Workbook
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
    needed_fields = ['OBJECTID','OBJECTID_1','Shape','Shape_Length','SHAPE', 'SHAPE_Length','thema',code]
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
    needed_fields = ['OBJECTID','OBJECTID_1', 'SHAPE', 'SHAPE_Length','Shape','Shape_Length','thema',code]
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

    arcpy.analysis.Intersect(
        in_features=invoer,
        out_feature_class=uitvoer,
        join_attributes="ALL",
        cluster_tolerance=0.1,
        output_type="POINT"
    )


    # arcpy.Intersect_analysis(invoer, uitvoer, "", clusterTolerance, "point")
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


def generate_profiles_onpoints(traject_punten,trajectlijn,profielen,code):


    # traject to points
    traject_punten = traject_punten
    trajectlijn = trajectlijn
    profiel_lengte_rivier = 100
    profiel_lengte_land = 100
    profielen = profielen
    code = code

    existing_fields = arcpy.ListFields(traject_punten)
    needed_fields = ["profielnummer","lengte_landzijde","lengte_rivierzijde"]
    for field in existing_fields:
        if field.name in needed_fields:
            arcpy.DeleteField_management(traject_punten, field.name)
    arcpy.AddField_management(traject_punten, "profielnummer", "DOUBLE", 2, field_is_nullable="NULLABLE")
    arcpy.AddField_management(traject_punten, "lengte_landzijde", "DOUBLE", 2, field_is_nullable="NULLABLE")
    arcpy.AddField_management(traject_punten, "lengte_rivierzijde", "DOUBLE", 2, field_is_nullable="NULLABLE")
    arcpy.CalculateField_management(traject_punten, "profielnummer", '!OBJECTID!', "PYTHON")
    arcpy.CalculateField_management(traject_punten, "lengte_landzijde", profiel_lengte_land, "PYTHON")
    arcpy.CalculateField_management(traject_punten, "lengte_rivierzijde", profiel_lengte_rivier, "PYTHON")

    # route voor trajectlijn
    # arcpy.CreateRoutes_lr(trajectlijn, code, "route_traject", "LENGTH", "", "", "UPPER_LEFT", "1", "0", "IGNORE", "INDEX")

    existing_fields = arcpy.ListFields(trajectlijn)
    needed_fields = ['OBJECTID', 'SHAPE', 'SHAPE_Length','Shape','Shape_Length',code]
    for field in existing_fields:
        if field.name not in needed_fields:
            arcpy.DeleteField_management(trajectlijn, field.name)
    arcpy.AddField_management(trajectlijn, "van", "DOUBLE", 2, field_is_nullable="NULLABLE")
    arcpy.AddField_management(trajectlijn, "tot", "DOUBLE", 2, field_is_nullable="NULLABLE")
    arcpy.CalculateField_management(trajectlijn, "van", 0, "PYTHON")
    arcpy.CalculateField_management(trajectlijn, "tot", "!Shape_Length!", "PYTHON")
    arcpy.CreateRoutes_lr(trajectlijn, code, 'route_traject', "TWO_FIELDS", "van", "tot", "", "1",
                          "0", "IGNORE", "INDEX")


    # locate profielpunten
    arcpy.LocateFeaturesAlongRoutes_lr(traject_punten, 'route_traject', code, "1.5 Meters", 'tabel_traject_punten',
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
    arcpy.CopyFeatures_management('deel_rivier', "temp_rivierdeel")
    arcpy.CopyFeatures_management('deel_land', "temp_landdeel")

    
    arcpy.AddField_management('temp_rivierdeel', "id", "DOUBLE", 2, field_is_nullable="NULLABLE")
    arcpy.AddField_management('temp_landdeel', "id", "DOUBLE", 2, field_is_nullable="NULLABLE")
    arcpy.CalculateField_management('temp_rivierdeel', "id", 2, "PYTHON")
    arcpy.CalculateField_management('temp_landdeel', "id", 1, "PYTHON")





    arcpy.Merge_management("'temp_rivierdeel';'temp_landdeel'", 'merge_profielpunten')
    arcpy.PointsToLine_management('merge_profielpunten', profielen, "profielnummer", "id", "NO_CLOSE")

    # arcpy.CalculateField_management(profielen, "van", 0, "PYTHON")
    # arcpy.CalculateField_management(profielen, "tot", "!Shape_Length!", "PYTHON")

    # arcpy.SpatialJoin_analysis(profielen, trajectlijn, 'profielen_temp', "JOIN_ONE_TO_ONE", "KEEP_ALL", match_option="INTERSECT")
    # arcpy.CopyFeatures_management('profielen_temp', profielen)
    # arcpy.FlipLine_edit(profielen)

    print ('profielen gemaakt op trajectlijn')


def excel_writer_factsheets_main(uitvoerpunten,code,excel,id,trajecten,toetspeil,min_plot,max_plot,trajectlijn,img,percelen_zone):

    # toetshoogte aan uitvoerpunten koppelen
    arcpy.JoinField_management(uitvoerpunten, code, trajecten, code, toetspeil)

    # binnenhalen van dataframe
    if toetspeil == 999:
        array = arcpy.da.FeatureClassToNumPyArray(uitvoerpunten,('OBJECTID', 'profielnummer', code, 'afstand', 'z_ahn', 'x', 'y'))
    else:
        array = arcpy.da.FeatureClassToNumPyArray(uitvoerpunten, ('OBJECTID', 'profielnummer', code, 'afstand', 'z_ahn', 'x', 'y', toetspeil))

    df = pd.DataFrame(array)
    df = df.dropna()
    sorted = df.sort_values(['profielnummer', 'afstand'], ascending=[True, True])

    # opbouw xlsx
    workbook = Workbook(excel)
    worksheet1 = workbook.add_worksheet('Overzicht')
    worksheet2 = workbook.add_worksheet()
    worksheet3 = workbook.add_worksheet('Perceelgegevens')
    # stijl toevoegen voor headers
    bold = workbook.add_format({'bold': True})


    # schrijf kolomnamen
    worksheet2.write(0, 0, "Profielnummer", bold)
    worksheet2.write(0, 1, "Afstand [m]", bold)
    worksheet2.write(0, 2, "Hoogte AHN3 [m NAP]", bold)
    worksheet2.write(0, 3, "x [RD]", bold)
    worksheet2.write(0, 4, "y [RD]", bold)

    # schrijf kolommen vanuit df
    worksheet2.write_column('A2', sorted['profielnummer'])
    worksheet2.write_column('B2', sorted['afstand'])
    worksheet2.write_column('C2', sorted['z_ahn'])
    worksheet2.write_column('D2', sorted['x'])
    worksheet2.write_column('E2', sorted['y'])

    # groepeer per profielnummer
    grouped = sorted.groupby('profielnummer')

    # definieer startrij
    startpunt = 2


    # lege lijngrafiek invoegen met zowel afstand als hoogte als invoer
    line_chart1 = workbook.add_chart({'type': 'scatter',
                                 'subtype': 'straight'})

    ## toetshoogte, aan/uit
    # toetshoogte toevoegen als horizontale lijn, deel 1 voor legenda
    # minimum = min(sorted['afstand'])
    # maximum = max(sorted['afstand'])
    # th = sorted[toetspeil].iloc[0]
    #
    # worksheet.write('K8', minimum)
    # worksheet.write('K9', maximum)
    # worksheet.write('K10', th)
    # worksheet.write('K11', th)


    # line_chart1.add_series({
    #     'name': 'toetshoogte: ' + str(th) + ' m NAP',
    #
    #     'categories': '=Sheet1!$K$8:$K$9',
    #     'values': '=Sheet1!$K$10:$K$11',
    #     'line': {
    #         'color': 'red',
    #         'width': 1.5,
    #         'dash_type': 'long_dash'
    #     }
    # })

    # lijnen toevoegen aan lijngrafiek
    count = 0
    for name, group in grouped:
        profielnaam = str(int(name))
        meetpunten = len(group['profielnummer'])

        # eerste profiel
        if count == 0:
            line_chart1.add_series({
                'name': 'profiel ' + profielnaam,

                'categories': '=Sheet2!B' + str(startpunt) + ':B' + str(meetpunten + 1),
                'values': '=Sheet2!C' + str(startpunt) + ':C' + str(meetpunten + 1),
                'line': {'width': 1}
            })
            count +=1
        # opvolgende profielen
        else:
            if count != 0 and name != 9999:
                line_chart1.add_series({
                    'name': 'profiel '+profielnaam,

                    'categories': '=Sheet2!B'+str(startpunt)+':B' + str(startpunt+meetpunten-1),
                    'values':     '=Sheet2!C'+str(startpunt)+':C' + str(startpunt+meetpunten-1),
                    'line': {'width': 1}
                })
            if name == 9999:
                line_chart1.add_series({
                    'name': 'maatgevend profiel',

                    'categories': '=Sheet2!B'+str(startpunt)+':B' + str(startpunt+meetpunten-1),
                    'values':     '=Sheet2!C'+str(startpunt)+':C' + str(startpunt+meetpunten-1),
                    'line': {
                        'color': 'red',
                        'width': 3
                    }
                })
        # startpunt verzetten
        startpunt += (meetpunten)



    ## toetshoogte toevoegen als horizontale lijn, deel 2 voor voorgrond-lijn
    # minimum = min(sorted['afstand'])
    # maximum = max(sorted['afstand'])
    # th = sorted[toetspeil].iloc[0]
    #
    # worksheet.write('K8', minimum)
    # worksheet.write('K9', maximum)
    # worksheet.write('K10', th)
    # worksheet.write('K11', th)
    #
    # line_chart1.add_series({
    #     'name': 'toetshoogte: ' + str(th) + ' m NAP',
    #
    #     'categories': '=Sheet1!$K$8:$K$9',
    #     'values': '=Sheet1!$K$10:$K$11',
    #     'line': {
    #         'color': 'red',
    #         'width': 1.5,
    #         'dash_type': 'long_dash'
    #     }
    # })

    # kolommen aanpassen
    line_chart1.set_title({'name': 'Overzicht profielen prio-vak '+id})
    line_chart1.set_x_axis({'name': 'Afstand [m]'})
    line_chart1.set_y_axis({'name': 'Hoogte [m NAP]'})
    line_chart1.set_x_axis({'interval_tick': 0.5})
    line_chart1.set_x_axis({'min': min_plot, 'max': max_plot})
    line_chart1.set_size({'width': 1000, 'height': 300})
    # line_chart1.set_style(1)
    worksheet1.insert_chart('D24', line_chart1) # alleen toevoegen voor toetshoogte

    # worksheet2.insert_chart('G3', line_chart1) # test
    worksheet2.hide()

    # schrijf parameters uit trajectlijn naar worksheet1
    # format worksheet
    cell_format_title = workbook.add_format()
    cell_format_title.set_font_size(16)
    cell_format_title.set_bold()

    cell_format_sub = workbook.add_format()
    cell_format_sub.set_pattern(1)
    cell_format_sub.set_bg_color('#e6e65c')
    cell_format_sub.set_bold()

    # stel kolom breedtes in
    worksheet1.set_column(0, 0, 30)
    worksheet1.set_column(1, 1, 60)
    worksheet3.set_column(0, 6, 15)



    # search cursor om er doorheen te gaan en parameters eruit te halen

    worksheet1.write('A1', "Factsheet prio-vak "+str(id), cell_format_title)

    worksheet1.write('A3', "", cell_format_sub)
    worksheet1.write('B4', "", cell_format_sub)
    worksheet1.write('B11', "", cell_format_sub)
    worksheet1.write('B15', "", cell_format_sub)
    worksheet1.write('B20', "", cell_format_sub)
    worksheet1.write('B24', "", cell_format_sub)

    worksheet1.write('B3', "waarde",cell_format_sub)


    worksheet1.write('A4', "Algemeen",cell_format_sub)
    worksheet1.write('A5', "Vaknummer")
    worksheet1.write('A6', "Van dijkpaal")
    worksheet1.write('A7', "Tot dijkpaal")
    worksheet1.write('A8', "Vaklengte [m]")
    worksheet1.write('A9', "Laatste versterking [traject]")
    worksheet1.write('A10', "Laatste versterking [jaar]")

    worksheet1.write('A11', "Basisgegevens techniek",cell_format_sub)
    worksheet1.write('A12', "Dikte deklaag gemiddeld [m]")
    worksheet1.write('A13', "Dik deklaag variatie [m]")
    worksheet1.write('A14', "Deformatie gemiddeld[mm/jaar]")

    worksheet1.write('A15', "Basisgegevens conditionering",cell_format_sub)
    worksheet1.write('A16', "Huizen binnen teenlijn [aantal]")
    worksheet1.write('A17', "Huizen +20m teenlijn [aantal]")
    worksheet1.write('A18', "Percelen binnen zone.. [aantal]")
    worksheet1.write('A19', "Leidingen [m]")
    worksheet1.write('A20', "Natura 2000")

    worksheet1.write('A21', "Beoordeling techniek",cell_format_sub)
    worksheet1.write('A22', "STPH [beta]")
    worksheet1.write('A23', "STBI [beta]")
    worksheet1.write('A24', "GEKB [beta]")

    worksheet1.write('A25', "Ontwerpproces",cell_format_sub)
    worksheet1.write('A26', "Groep VVK")
    worksheet1.write('A27', "Maatregel VVK [soort]")
    worksheet1.write('A28', "Kosten VVK [*miljoen euro]")
    worksheet1.write('A29', "Extra sonderingen [aantal]")
    worksheet1.write('A30', "Extra boringen [aantal]")

    worksheet1.write('A31', "Geometrie")

    # maak array-pandas df van trajectlijn
    velden = ["prio_nummer","Van","Tot","Shape_Length","TRAJECT","OPLEVERING","gem_dpip","var_dpip","gem_zet","panden_dijkzone", "panden_dijkzone_bit",
              "lengte_kl", "extra_bo", "extra_so", "gekb_2023","stbi_2023","stph_2023","na2000","extra_inmeten","maatregel","kosten","groep","percelen_zone"]
    array_fact = arcpy.da.FeatureClassToNumPyArray(trajectlijn,velden)
    df_fact= pd.DataFrame(array_fact)


    nummer = df_fact['prio_nummer'].iloc[0]
    van = df_fact['Van'].iloc[0]
    tot = df_fact['Tot'].iloc[0]
    lengte = int(df_fact['Shape_Length'].iloc[0])

    # test op NaN

    traject = df_fact['TRAJECT'].iloc[0]
    oplevering = df_fact['OPLEVERING'].iloc[0]
    gdpip = df_fact['gem_dpip'].iloc[0]
    vdpip = df_fact['var_dpip'].iloc[0]
    gzet = df_fact['gem_zet'].iloc[0]
    pdijk = df_fact['panden_dijkzone'].iloc[0]
    pbit = df_fact['panden_dijkzone_bit'].iloc[0]
    lengtekl = df_fact['lengte_kl'].iloc[0]
    na2000 = df_fact['na2000'].iloc[0]
    stph = df_fact['stph_2023'].iloc[0]
    stbi = df_fact['stbi_2023'].iloc[0]
    gekb = df_fact['gekb_2023'].iloc[0]
    groep = df_fact['groep'].iloc[0]
    kosten = df_fact['kosten'].iloc[0]
    maatregel = df_fact['maatregel'].iloc[0]
    extrabo = int(df_fact['extra_bo'].iloc[0])
    extraso = int(df_fact['extra_so'].iloc[0])
    extrameet= df_fact['extra_inmeten'].iloc[0]
    percelen = df_fact['percelen_zone'].iloc[0]




    # schrijf parameters naar de excelcellen
    worksheet1.write('B5',  nummer)
    worksheet1.write('B6', van)
    worksheet1.write('B7', tot)
    worksheet1.write('B8', str(lengte))

    if str(traject) == "None":
        worksheet1.write('B9', "n.v.t.")
    else:
        worksheet1.write('B9', traject)


    if str(oplevering) == "None":
        worksheet1.write('B10', "n.v.t.")
    else:
        worksheet1.write('B10', oplevering)

    if pd.isna(gdpip) == True:
        worksheet1.write('B12', "n.v.t.")
    else:
        gdpip = round(gdpip, 1)
        worksheet1.write('B12', str(gdpip))

    if pd.isna(vdpip) == True:
        worksheet1.write('B13', "n.v.t.")
    else:
        vdpip = round(vdpip, 1)
        worksheet1.write('B13', str(vdpip))


    if pd.isna(gzet) == True:
        worksheet1.write('B14', "n.v.t.")
    else:
        gzet = round(gzet, 1)
        worksheet1.write('B14', str(gzet))




    if pdijk > 0:
        pdijk = int(pdijk)
        worksheet1.write('B16', str(pdijk))
    else:
        worksheet1.write('B16', "n.v.t.")

    if pbit > 0:
        pbit = int(pbit)
        worksheet1.write('B17', str(pbit))
    else:
        worksheet1.write('B17', "n.v.t.")

    if percelen > 0:
        percelen = int(percelen)
        worksheet1.write('B18', str(percelen))
    else:
        worksheet1.write('B18', "n.v.t.")


    if pd.isna(lengtekl) == True:
        worksheet1.write('B19', "n.v.t.")
    else:
        lengtekl = int(lengtekl)
        worksheet1.write('B19', str(lengtekl))


    if na2000 == "Ja":
        worksheet1.write('B20', "Aanwezig")
    else:
        worksheet1.write('B20', "n.v.t.")

    if pd.isna(stph) == True:
        worksheet1.write('B22', "n.v.t.")
    else:
        stph = round(stph, 1)
        worksheet1.write('B22', str(stph))

    if pd.isna(stbi) == True:
        worksheet1.write('B23', "n.v.t.")
    else:
        stbi = round(stbi, 1)
        worksheet1.write('B23', str(stbi))

    if pd.isna(gekb) == True:
        worksheet1.write('B24', "n.v.t.")
    else:
        gekb = round(gekb, 1)
        worksheet1.write('B24', str(gekb))



    if pd.isna(groep) == True:
        worksheet1.write('B26', "n.v.t.")
    else:
        worksheet1.write('B26', str(groep))

    if pd.isna(maatregel) == True:
        worksheet1.write('B27', "n.v.t.")
    else:
        worksheet1.write('B27', str(maatregel))



    if pd.isna(kosten) == True:
        worksheet1.write('B28', "Onbekend")
    else:
        worksheet1.write('B28', str(kosten))



    if pd.isna(extraso) == True or extraso < 1:
        worksheet1.write('B29', "n.v.t.")
    else:
        extrago = int(extraso)
        worksheet1.write('B29', str(extraso))

    if pd.isna(extrabo) == True or extrabo < 1:
        worksheet1.write('B30', "n.v.t.")
    else:
        extrago = int(extrabo)
        worksheet1.write('B30', str(extrabo))

    if extrameet == "Ja":
        worksheet1.write('B31', "Extra inmetingen vereist")
    else:
        worksheet1.write('B31', "Geen inmetingen vereist")


    # insert plot vanuit arcmap
    worksheet1.insert_image('D3', img)




    ## voeg perceeldata toe aan nieuwe sheet

    # data binnenhalen
    velden_percelen = ["OBJECTID","Huisnummer","Huisletter","Postcode","OpenbareRuimteNaam","WoonplaatsNaam"]
    array_percelen = arcpy.da.FeatureClassToNumPyArray(percelen_zone, velden_percelen, null_value=-9999)
    df = pd.DataFrame(array_percelen)
    df_percelen = df.sort_values('OpenbareRuimteNaam', ascending=False)

    # kolomnamen
    worksheet3.write('A1', "OBJECTID_gis", cell_format_sub)
    worksheet3.write('B1', "Straatnaam", cell_format_sub)
    worksheet3.write('C1', "Huisnummer", cell_format_sub)
    worksheet3.write('D1', "Huisletter", cell_format_sub)
    worksheet3.write('E1', "Postcode", cell_format_sub)
    worksheet3.write('F1', "Plaatsnaam", cell_format_sub)

    # schrijven kolommen
    worksheet3.write_column('A2', df_percelen['OBJECTID'])
    worksheet3.write_column('B2', df_percelen['OpenbareRuimteNaam'])
    worksheet3.write_column('C2', df_percelen['Huisnummer'])
    worksheet3.write_column('D2', df_percelen['Huisletter'])
    worksheet3.write_column('E2', df_percelen['Postcode'])
    worksheet3.write_column('F2', df_percelen['WoonplaatsNaam'])


    workbook.close()
    del df
    del df_percelen
    del df_fact




    # print *'.xlsx-bestand gemaakt voor factsheet'



def calculate_absolute_difference(a, b):
    if a is not None and b is not None:
        return (a+b)/2
    elif a is not None:
        return a
    elif b is not None:
        return b
    else:
        return None
