import arcpy
from base import *

arcpy.env.overwriteOutput = True
arcpy.env.workspace = r"C:\Users\vince\Documents\ArcGIS\Projects\safe uittredepunten\safe uittredepunten.gdb"

trajectlijnTotaal = "safe_buitenkruinlijn_wsrl"
vakindelingStph = "vakindeling_stph"
uittredePunten = "stph_punten"
lijnInterval = 10
filterInterval = 5
lengteProfielen = 300
profielBuffer = 10
profielCode = "OBJECTID"
veldenPunten = ["kleurcode","kleur"]
profielen_selectie = "profielen_selectie"

def deel_1():
    # split trajectlijn in delen
    arcpy.management.GeneratePointsAlongLines("safe_buitenkruinlijn_wsrl", "trajectlijn_splitpoints", "DISTANCE", "{} Meters".format(lijnInterval), None, None)
    arcpy.management.SplitLineAtPoint("safe_buitenkruinlijn_wsrl", "trajectlijn_splitpoints", "trajectlijn_splits", "0.1 Meters")

    # maak profielen op gewenste interval
    arcpy.management.GenerateTransectsAlongLines("safe_buitenkruinlijn_wsrl", "trajectlijn_profielen_nofilter", "{} Meters".format(filterInterval), "{} Meters".format(lengteProfielen), "END_POINTS")

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

        # testcursor = arcpy.da.SearchCursor("uittredepunten",["Vaknaam"])
        # for trow in testcursor:
        #     print (trow[0])


        arcpy.management.SelectLayerByLocation("uittredepunten", "INTERSECT", "temp_profiel_buffer", None, "NEW_SELECTION", "NOT_INVERT")
        arcpy.CopyFeatures_management("uittredepunten", "temp_selectie_punten")

        # selecteer laagte beta en koppel kleur terug aan profiel
        npArray = arcpy.da.FeatureClassToNumPyArray("temp_selectie_punten",veldenPunten)
        profiel_df = pd.DataFrame(npArray)
        try:
            minBeta = profiel_df[profiel_df.kleurcode == profiel_df.kleurcode.min()].iloc[0]['kleurcode']
            minKleur = profiel_df[profiel_df.kleurcode == profiel_df.kleurcode.min()].iloc[0]['kleur']
            row[2] = minKleur
            profielCursor.updateRow(row)
            print (minBeta,minKleur)
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

# deel_1()
deel_2()
deel_3()











