# generate profiles or get profile input

import arcpy
from base import *

arcpy.env.overwriteOutput = True
arcpy.env.workspace = r"C:\Users\vince\Documents\ArcGIS\Projects\kabels en leidingen ssh\test.gdb"

offsetTrajectory = 10
newProfiles = True
trajectlijn = "testsectie"
profielen = "profielen_{}".format(trajectlijn)
profiel_interval = 50
profiel_lengte_land = 100
profiel_lengte_rivier = 100
code = "deeltraject"
stapgrootte_punten = 0.5
raster = r"C:\Users\vince\Desktop\werk\Projecten\WSRL\sterreschans_heteren\GIS\waterlopen300m.gdb\ahn3clipsh1"

intersectingLayers = ["merge_r_d", "merge_w_d"]

# temp variables
invoerpunten = "punten_profielen"
uitvoerpunten = "punten_profielen_z"




if newProfiles is True:
    copy_trajectory_lr(trajectlijn,code,offsetTrajectory)
    generate_profiles(profiel_interval,profiel_lengte_land,profiel_lengte_rivier,trajectlijn,code,profielen)
    set_measurements_trajectory(profielen,trajectlijn,code,stapgrootte_punten)
    extract_z_arcpy(invoerpunten, uitvoerpunten, raster)
    add_xy(uitvoerpunten,code,trajectlijn)

    # loop through intersectingslayers do action if intersects with profiel:
    # get nearest afstand, z and profile number
    # put in array
    # 



else:
    copy_trajectory_lr(trajectlijn,code,offsetTrajectory)
    set_measurements_trajectory(profielen,trajectlijn,code,stapgrootte_punten)
    extract_z_arcpy(invoerpunten, uitvoerpunten, raster)
    add_xy(uitvoerpunten,code,trajectlijn)



# get input for intersecting layers
# find and locate intersects
# write all data to seperate excels

