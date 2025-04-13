import arcpy
from base import *

arcpy.env.overwriteOutput = True
arcpy.env.workspace = r"C:\Users\vince\Mijn Drive\WSRL\safe_data\safe_data\safe_data.gdb"

traject_punten = "leo_go_2002024_locs"
trajectlijn = "trajectlijn_safe_rd"
profielen = "profielen_leo_go_2002024"
code = "code"
generate_profiles_onpoints(traject_punten,trajectlijn,profielen,code)