import arcpy
from base import *

arcpy.env.overwriteOutput = True
arcpy.env.workspace = r"C:\Users\vince\Mijn Drive\WSRL\safe_data\safe_data\safe_data.gdb"

traject_punten = "belendingen_centroid_points"
trajectlijn = "trajectlijn_safe_rd"
profielen = "puflocs_nietprio_profiles_21082023"
code = "code"
generate_profiles_onpoints(traject_punten,trajectlijn,profielen,code)