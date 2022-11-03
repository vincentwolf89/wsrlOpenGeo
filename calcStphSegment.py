import arcpy

arcpy.env.overwriteOutput = True
arcpy.env.workspace = r"C:\Users\vince\Documents\ArcGIS\Projects\safe uittredepunten\safe uittredepunten.gdb"

trajectlijnTotaal = "safe_buitenkruinlijn_wsrl"
lijnInterval = 10
filterInterval = 5
lengteProfielen = 150


# split trajectlijn in delen
arcpy.management.GeneratePointsAlongLines("safe_buitenkruinlijn_wsrl", "trajectlijn_splitpoints", "DISTANCE", "{} Meters".format(lijnInterval), None, None)
arcpy.management.SplitLineAtPoint("safe_buitenkruinlijn_wsrl", "trajectlijn_splitpoints", "trajectlijn_splits", None)

# maak profielen op gewenste interval
arcpy.management.GenerateTransectsAlongLines("safe_buitenkruinlijn_wsrl", "trajectlijn_profielen_nofilter", "{} Meters".format(filterInterval), "{} Meters".format(lengteProfielen), "NO_END_POINTS")

# selecteer profielen zonder intersect met punten 
arcpy.MakeFeatureLayer_management("trajectlijn_profielen_nofilter", "templayer") 
arcpy.management.SelectLayerByLocation("templayer", "INTERSECT", "trajectlijn_splitpoints", None, "NEW_SELECTION", "INVERT")
arcpy.CopyFeatures_management("templayer", "trajectlijn_profielen_filter")

# split profielen op trajectlijn
arcpy.management.SplitLineAtPoint("trajectlijn_profielen_filter", "trajectlijn_splitpoints", "profielen_splits", None)


# selecteer alleen landzijde profieldeel
arcpy.MakeFeatureLayer_management("profielen_splits", "templayer") 
arcpy.management.SelectLayerByAttribute("templayer", "NEW_SELECTION", "ORIG_SEQ = 1", None)
arcpy.CopyFeatures_management("templayer", "profielen_landzijde")

# selecteer relevante profielen voor berekening (vakindeling stph)

# bereken profiel oordeel

# koppel profiel oordeel aan lijnsegment