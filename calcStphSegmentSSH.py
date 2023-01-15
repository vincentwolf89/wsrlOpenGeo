import arcpy
from base import *

arcpy.env.overwriteOutput = True
arcpy.env.workspace = r"C:\Users\vince\Documents\ArcGIS\Projects\beoordeling ssh\beoordeling ssh.gdb"

trajectlijnTotaal = "ssh_spst_traject"
vakindelingStph = "vakindeling_stph"
uittredePunten = "temp_uittredepunten_stph"
lijnInterval = 10
filterInterval = 5
lengteProfielen = 300
profielBuffer = 10
profielCode = "OBJECTID"
veldenPunten = ["Beta_prob","Categorie_prob"]
profielen_selectie = "profielen_selectie"
invoer_tabel = r"C:\Users\vince\Documents\ArcGIS\Projects\beoordeling ssh\input\stph\invoer_stph.xlsx"
xField = "X_uittrede"
yField = "Y_uittrede"
betaField = "Beta_prob"
catField = "Categorie_prob"
eindOordeelLijn = "eindoordeel_stph"
categoriesInSufficient = ["IV","V","VI"]

def importeer_tabel():
    arcpy.conversion.ExcelToTable(invoer_tabel, "temp_stph_table", "Sheet1")
    arcpy.management.XYTableToPoint("temp_stph_table", uittredePunten, xField, yField, None, 'PROJCS["RD_New",GEOGCS["GCS_Amersfoort",DATUM["D_Amersfoort",SPHEROID["Bessel_1841",6377397.155,299.1528128]],PRIMEM["Greenwich",0.0],UNIT["Degree",0.0174532925199433]],PROJECTION["Double_Stereographic"],PARAMETER["False_Easting",155000.0],PARAMETER["False_Northing",463000.0],PARAMETER["Central_Meridian",5.38763888888889],PARAMETER["Scale_Factor",0.9999079],PARAMETER["Latitude_Of_Origin",52.15616055555555],UNIT["Meter",1.0]];-30515500 -30279500 10000;-100000 10000;-100000 10000;0.001;0.001;0.001;IsHighPrecision')

def deel_1():
    # split trajectlijn in delen
    arcpy.management.GeneratePointsAlongLines(trajectlijnTotaal, "trajectlijn_splitpoints", "DISTANCE", "{} Meters".format(lijnInterval), None, None)
    arcpy.management.SplitLineAtPoint(trajectlijnTotaal, "trajectlijn_splitpoints", "trajectlijn_splits", "0.1 Meters")

    # maak profielen op gewenste interval
    arcpy.management.GenerateTransectsAlongLines(trajectlijnTotaal, "trajectlijn_profielen_nofilter", "{} Meters".format(filterInterval), "{} Meters".format(lengteProfielen), "END_POINTS")

    # selecteer profielen zonder intersect met punten 
    arcpy.MakeFeatureLayer_management("trajectlijn_profielen_nofilter", "templayer") 
    arcpy.management.SelectLayerByLocation("templayer", "INTERSECT", "trajectlijn_splitpoints", None, "NEW_SELECTION", "INVERT")
    arcpy.CopyFeatures_management("templayer", "trajectlijn_profielen_filter")

    # split profielen op trajectlijn
    arcpy.analysis.Intersect([trajectlijnTotaal,"trajectlijn_profielen_filter"], "temp_splitpoints_profielen", "ALL", None, "POINT")
    arcpy.management.SplitLineAtPoint("trajectlijn_profielen_filter", "temp_splitpoints_profielen", "profielen_splits", "0.1 Meters")


    # selecteer alleen landzijde profieldeel
    copy_trajectory_lr(trajectlijn=trajectlijnTotaal,code=0,afstand=5)
    arcpy.MakeFeatureLayer_management("profielen_splits", "templayer") 
    arcpy.management.SelectLayerByLocation("templayer", "INTERSECT", "land", None, "NEW_SELECTION", "NOT_INVERT")
    arcpy.CopyFeatures_management("templayer", "profielen_landzijde")

    # selecteer relevante profielen voor berekening (vakindeling stph)
    arcpy.MakeFeatureLayer_management("profielen_landzijde", "templayer")
    arcpy.management.SelectLayerByLocation("templayer", "INTERSECT", vakindelingStph, "5 Meters", "NEW_SELECTION", "NOT_INVERT") 
    arcpy.CopyFeatures_management("templayer", "profielen_selectie")
    arcpy.AddField_management("profielen_selectie", "eindoordeel", "TEXT", 2)


def deel_2():
# bereken profiel oordeel
# itereer over profielen
    profielCursor = arcpy.da.UpdateCursor(profielen_selectie,['SHAPE@','OBJECTID','eindoordeel'])
    for row in profielCursor:
        id = row[1]
        where = '"' + profielCode + '" = {}'.format(str(id))
        arcpy.Select_analysis(profielen_selectie, "temp_profiel", where)

        # buffer profiel beide kanten
        arcpy.analysis.Buffer("temp_profiel", "temp_profiel_buffer", "{} Meters".format(profielBuffer), "FULL", "ROUND", "NONE", None, "PLANAR")

        # selecteer alle punten binnen buffer
        arcpy.MakeFeatureLayer_management(uittredePunten, "uittredepunten") 



        arcpy.management.SelectLayerByLocation("uittredepunten", "INTERSECT", "temp_profiel_buffer", None, "NEW_SELECTION", "NOT_INVERT")
        arcpy.CopyFeatures_management("uittredepunten", "temp_selectie_punten")

        # selecteer laagte beta en koppel kleur terug aan profiel
        npArray = arcpy.da.FeatureClassToNumPyArray("temp_selectie_punten",veldenPunten)
        profiel_df = pd.DataFrame(npArray)
        print (profiel_df)
        try:
            minBeta = profiel_df[profiel_df[betaField] == profiel_df[betaField].min()].iloc[0][betaField]
            minCat = profiel_df[profiel_df[betaField] == profiel_df[betaField].min()].iloc[0][catField]
            row[2] = minCat
            profielCursor.updateRow(row)
            print (minBeta)
        except Exception:
            print (Exception)
        
        # break
    del profielCursor
 

def deel_3():
    # verwijder nul waardes uit profielen
    arcpy.CopyFeatures_management(profielen_selectie, "profielen_selectie_filter")
    profielCursor = arcpy.da.UpdateCursor("profielen_selectie_filter",['SHAPE@','OBJECTID','eindoordeel'])
    for row in profielCursor:
        if row[2] is None:
            profielCursor.deleteRow()
        else:
            pass


    # koppel waardes aan splits
    arcpy.analysis.SpatialJoin("trajectlijn_splits", "profielen_selectie_filter", "splits_join", "JOIN_ONE_TO_ONE", "KEEP_ALL", "","CLOSEST", "10 Meters", '')
    # selecteer splits o.b.v. trajectlijn
    arcpy.MakeFeatureLayer_management("splits_join", "temp_splits_join") 
    arcpy.management.SelectLayerByLocation("temp_splits_join", "INTERSECT", vakindelingStph, "10 Meters", "NEW_SELECTION", "NOT_INVERT")
    arcpy.CopyFeatures_management("temp_splits_join", "splits_vakindeling")

    # selecteer delen zonder oordeel en koppel deze aan dichstbijzijnde deel met oordeel
    arcpy.MakeFeatureLayer_management("splits_vakindeling", "temp_splits_vakindeling_null") 
    arcpy.management.SelectLayerByAttribute("temp_splits_vakindeling_null", "NEW_SELECTION", "eindoordeel IS NULL", None)
    arcpy.CopyFeatures_management("temp_splits_vakindeling_null", "splits_vakindeling_null")

    arcpy.MakeFeatureLayer_management("splits_vakindeling", "temp_splits_vakindeling_not_null") 
    arcpy.management.SelectLayerByAttribute("temp_splits_vakindeling_not_null", "NEW_SELECTION", "eindoordeel IS NOT NULL", None)
    arcpy.CopyFeatures_management("temp_splits_vakindeling_not_null", "splits_vakindeling_not_null")

    arcpy.analysis.SpatialJoin("splits_vakindeling_null", "splits_vakindeling_not_null", "temp_join", "JOIN_ONE_TO_ONE", "KEEP_ALL", "", "CLOSEST", None, '')
    arcpy.management.JoinField("splits_vakindeling_null", "OBJECTID", "temp_join", "OBJECTID", "eindoordeel_1", "NOT_USE_FM", None)
    # arcpy.management.JoinField("splits_vakindeling_null", "OBJECTID", "temp_join", "OBJECTID", "eindoordeel_1", "NOT_USE_FM", None)
    arcpy.DeleteField_management("splits_vakindeling_null", ["eindoordeel"])
    arcpy.management.AlterField("splits_vakindeling_null", "eindoordeel_1", "eindoordeel")

    # merge datasets
    arcpy.Merge_management(["splits_vakindeling_null","splits_vakindeling_not_null"], eindOordeelLijn)

    # bereken eindoordeel
    arcpy.AddField_management(eindOordeelLijn, "eindoordeel_final", "TEXT", 2)
    oordeelCursor = arcpy.da.UpdateCursor(eindOordeelLijn,["eindoordeel","eindoordeel_final"])
    for oordeelRow in oordeelCursor:
        finalOordeel = "voldoende"
        for oordeel in categoriesInSufficient:
            
            if oordeelRow[0].startswith(oordeel):
                finalOordeel = "onvoldoende"
                break

        oordeelRow[1] = finalOordeel
        oordeelCursor.updateRow(oordeelRow)

    
        

# importeer_tabel()
# deel_1()
# deel_2()
deel_3()











