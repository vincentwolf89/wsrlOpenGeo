import arcpy
from base import *

arcpy.env.overwriteOutput = True
arcpy.env.workspace = r"C:\Users\vince\Documents\ArcGIS\Projects\schets nelle\schets nelle.gdb"

traject_punten = "stbi_profile_locs"
trajectlijn = "trajectlijn_safe_rd"
profielen = "stbi_profiles"
code = "code"
generate_profiles_onpoints(traject_punten,trajectlijn,profielen,code)