import arcpy
from base import *

arcpy.env.overwriteOutput = True
arcpy.env.workspace = r"C:\Users\vince\Documents\ArcGIS\Projects\safe aanpassingen scope lijnen\repaired.gdb"

traject_punten = "pufloc_points_new"
trajectlijn = "trajectlijn_safe_rd"
profielen = "pufloc_profiles"
code = "code"
generate_profiles_onpoints(traject_punten,trajectlijn,profielen,code)