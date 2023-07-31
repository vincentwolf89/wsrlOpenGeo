import arcpy
from base import *

arcpy.env.overwriteOutput = True
arcpy.env.workspace = r"C:\Users\vince\Documents\ArcGIS\Projects\safe aanpassingen scope lijnen\repaired.gdb"

traject_punten = "puflocs_15072023"
trajectlijn = "trajectlijn_safe_rd"
profielen = "puflocs_profiles_15072023"
code = "code"
generate_profiles_onpoints(traject_punten,trajectlijn,profielen,code)