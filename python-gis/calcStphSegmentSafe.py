import arcpy
from base import *

arcpy.env.overwriteOutput = True
arcpy.env.workspace = r"C:\Users\vince\Mijn Drive\WSRL\safe_data\safe_data\tempdata.gdb"

trajectlijnTotaal = r"C:\Users\vince\Mijn Drive\WSRL\safe_data\safe_data\safe_data.gdb\safe_buitenkruinlijn_wsrl"
vakindelingStph = r"C:\Users\vince\Mijn Drive\WSRL\safe_data\safe_data\safe_data.gdb\vakindeling_stph_23072023_select_rd"
uittredePunten = r"C:\Users\vince\Mijn Drive\WSRL\safe_data\safe_data\safe_data.gdb\stph_24082023_punten_rd"
lijnInterval = 10
filterInterval = 5
lengteProfielen = 300
profielBuffer = 10
profielCode = "OBJECTID"
betaField = "Beta_prob_agg"
catField = "Categorie_prob"
veldenPunten = ["Beta_prob_agg","Categorie_prob"] #["kleurcode","kleur"]
profielen_selectie = "profielen_selectie"
invoer_tabel = r"C:\Users\vince\Desktop\safe_temp\Kleuren_opgave_totaal.xlsx"

# output
outputVakindeling = "C:/Users/vince/Mijn Drive/WSRL/safe_data/safe_data/safe_data.gdb/{}_updated".format(vakindelingStph)

def importeer_tabel():
    arcpy.conversion.ExcelToTable(invoer_tabel, "tabel_nieuw", "Sheet1")

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
    profielCursor = arcpy.da.UpdateCursor(profielen_selectie,['SHAPE@','OBJECTID','eindoordeel','min_beta'])
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
            # minBeta = profiel_df[profiel_df.kleurcode == profiel_df.kleurcode.min()].iloc[0]['kleurcode']
            # minKleur = profiel_df[profiel_df.kleurcode == profiel_df.kleurcode.min()].iloc[0]['kleur']
            
            # row[2] = minKleur
            # profielCursor.updateRow(row)
            # print (minBeta,minKleur)

            minBeta = profiel_df[profiel_df[betaField] == profiel_df[betaField].min()].iloc[0][betaField]
            minCat = profiel_df[profiel_df[betaField] == profiel_df[betaField].min()].iloc[0][catField]
            row[2] = minCat
            row[3] = minBeta
            profielCursor.updateRow(row)
            print (minBeta, minCat)
        except Exception:

            row[2] = None
            profielCursor.updateRow(row)
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
    print ("all done...")

# new part for safe to get back to the line segments, use groupby to get it or something
def deel_4():
    # copy to new layer
    arcpy.CopyFeatures_management(vakindelingStph, outputVakindeling)
    # add field
    arcpy.AddField_management(outputVakindeling, "minbeta_vak", "DOUBLE", 2, field_is_nullable="NULLABLE")
    # iterate over segments
    segmentCursor = arcpy.da.UpdateCursor(outputVakindeling,['SHAPE@','OBJECTID','minbeta_vak'])
    for row in segmentCursor:
        id = row[1]
        where = '"' + profielCode + '" = {}'.format(str(id))
        arcpy.Select_analysis(outputVakindeling, "temp_section", where)


        # select profiles by location with sjoin
        arcpy.analysis.SpatialJoin(
            target_features=profielen_selectie,
            join_features="temp_section",
            out_feature_class="temp_section_profiles",
            join_operation="JOIN_ONE_TO_ONE",
            join_type="KEEP_COMMON",
            match_option="INTERSECT",
            search_radius="1 Meters",
        )

        profileCursor = arcpy.da.SearchCursor("temp_section_profiles",["min_beta"])
        scores = []
        for pRow in profileCursor:
            if pRow[0] is not None:
                scores.append(pRow[0])

        try:
            minScore = min(scores)
            row[2] = minScore
            segmentCursor.updateRow(row)
            print (minScore)

        except Exception:
            print ("error")
            pass




# importeer_tabel()
# deel_1()
# deel_2()
# deel_3()
deel_4()