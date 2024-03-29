# generate profiles or get profile input
from xlsxwriter.workbook import Workbook


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
profileNumberField = "profielnummer"
isectNumberField = "OBJECTID"
profileFields = ["profielnummer"]

subTypeField = "thema"
diameterField = "diameter"
pressureField = "druk"
materialField = "label"

isectFields = [isectNumberField,profileNumberField,subTypeField]
isectFieldsKL = [isectNumberField,profileNumberField,subTypeField,diameterField,pressureField,materialField]

isectDfColumns = ["type","afstand","hoogte","diameter","druk","materiaal"]
elevationSourceName = "AHN3"
fieldsProfile = ["profielnummer","afstand","z_ahn","x","y"]
plotLocation= "C:/Users/vince/Desktop/temp/"
isectPlotElevation = 4

# def diameter, druk, materiaalsoort


klThemes = ["riool","water"]

layersForIntersects = {
    "riool": {
        "name":"merge_r_d_rd",
        "symbol":"circle",
    },
    "water": {
        "name":"merge_w_d_rd",
        "symbol":"circle",
    },
    "kruinlijn": {
        "name":"testsectie",
        "symbol":"square",
    },
  
}

colorsForIntersects = {
  "rioolVrijverval": "blue",
  "rioolOnderOverOfOnderdruk":"yellow",
  "water": "blue",
  "buitenkruin":"orange"
}


# temp variables
invoerpunten = "punten_profielen"
uitvoerpunten = "punten_profielen_z"

def createProfileSheet(sheetName, profilePoints , isectPoints):
    
    workbook = Workbook(plotLocation+sheetName+".xlsx")
    worksheet1 = workbook.add_worksheet('Overzicht')
    # worksheet2 = workbook.add_worksheet()

    # style for headers
    bold = workbook.add_format({'bold': True})

    # write column headers
    # worksheet1.write(0, 0, "Profielnummer", bold)
    worksheet1.write(0, 0, "Profielnummer", bold)
    worksheet1.write(0, 1, "Afstand [m]", bold)
    worksheet1.write(0, 2, "Hoogte {} [m NAP]".format(elevationSourceName), bold)
    worksheet1.write(0, 3, "x [RD]", bold)
    worksheet1.write(0, 4, "y [RD]", bold)

    worksheet1.write(0, 5, "Type", bold)
    worksheet1.write(0, 6, "Subtype", bold)
    worksheet1.write(0, 7, "Afstand", bold)
    worksheet1.write(0, 8, "Hoogte", bold)
    worksheet1.write(0, 9, "Diameter", bold)
    worksheet1.write(0, 10, "Druk", bold)
    worksheet1.write(0, 11, "Materiaal", bold)

    # write colums
    worksheet1.write_column('A2', profilePoints['profielnummer'])
    worksheet1.write_column('B2', profilePoints['afstand'])
    worksheet1.write_column('C2', profilePoints['z_ahn'])
    worksheet1.write_column('D2', profilePoints['x'])
    worksheet1.write_column('E2', profilePoints['y'])

    worksheet1.write_column('F2', isectPoints['type'])
    worksheet1.write_column('G2', isectPoints['subtype'])
    worksheet1.write_column('H2', isectPoints['afstand'])
    worksheet1.write_column('I2', isectPoints['hoogte'])
    
    worksheet1.write_column('J2', isectPoints['diameter'])
    worksheet1.write_column('K2', isectPoints['druk'])
    worksheet1.write_column('L2', isectPoints['materiaal'])

    # definieer startrij
    startpunt = 2

    # lege lijngrafiek invoegen met zowel afstand als hoogte als invoer
    line_chart1 = workbook.add_chart({'type': 'scatter',
                                 'subtype': 'straight'})

    meetpunten = len(profilePoints['profielnummer'])
    line_chart1.add_series({
        'name': '{}-profiel'.format(elevationSourceName),
        'categories': '=Overzicht!B'+str(startpunt)+':B' + str(startpunt+meetpunten-1),
        'values':     '=Overzicht!C'+str(startpunt)+':C' + str(startpunt+meetpunten-1),
        'line': {'width': 1}
    })

    line_chart1.set_title({'name': 'Overzicht {}'.format(sheetName)})
    line_chart1.set_x_axis({'name': 'Afstand [m]'})
    line_chart1.set_y_axis({'name': 'Hoogte [m NAP]'})
    line_chart1.set_x_axis({'interval_tick': 0.5})
    # line_chart1.set_x_axis({'min': min_plot, 'max': max_plot})
    line_chart1.set_size({'width': 1000, 'height': 300})
    line_chart1.set_style(1)
    
    worksheet1.insert_chart('D24', line_chart1) 

    # iterate over isectPoints and create separate series for each intersect
    indexes = []
    seriesInChart = {}
    for index, row in isectPoints.iterrows():
   
        rowIndex = str(index+2)
        layerType = row['type']
        

        line_chart1.add_series({
            'name': row['subtype'],
            'categories': '=Overzicht!$H${}:$H${}'.format(rowIndex,rowIndex),
            'values':     '=Overzicht!$I${}:$I${}'.format(rowIndex,rowIndex),
            # 'y_error_bars': {
            #     'type': 'fixed',
            #     'value': 5,
            #     'end_style': 0,
            #     'direction': 'plus',
            #     'color':'yellow'
            # },
            'line':   {'none': True},
            'marker': {
                'type': layersForIntersects[layerType]["symbol"],
                'size': 8,
                'border': {'none': True},
                'fill':   {'color': colorsForIntersects[row['subtype']]},
            },
            # 'data_labels': {'value': True, 'legend_key': True},
        })


        indexes.append(index+1)
        seriesInChart[index+1] = row['subtype']
    
    
    # remove duplicates from legend
    rev_dict = {}
    for key, value in seriesInChart.items():
        rev_dict.setdefault(value, set()).add(key)
        
    result = [key for key, values in rev_dict.items()
                                if len(values) > 1]
    
    duplicates = []
    for value in result:
        key = [k for k, v in seriesInChart.items() if v == value][0]
        duplicates.append(key)
    
    line_chart1.set_legend({'delete_series': duplicates})

    workbook.close()




if newProfiles is True:
    # copy_trajectory_lr(trajectlijn,code,offsetTrajectory)
    # generate_profiles(profiel_interval,profiel_lengte_land,profiel_lengte_rivier,trajectlijn,code,profielen)
    # set_measurements_trajectory(profielen,trajectlijn,code,stapgrootte_punten)
    # extract_z_arcpy(invoerpunten, uitvoerpunten, raster)
    # add_xy(uitvoerpunten,code,trajectlijn)

    

    # loop through profielen and check for 
    profielCursor = arcpy.da.SearchCursor(profielen, profileFields)
    for profile in profielCursor:

        # create array for isects
        isectDf = pd.DataFrame(columns = isectDfColumns)

        # create templayer
        profileNumber = int(profile[0])
        where = '"' + profileNumberField + '" = ' + str(profileNumber)
        temp_profile = "temp_profile"
        arcpy.Select_analysis(profielen, temp_profile, where)
        arcpy.Select_analysis(uitvoerpunten, "temp_uitvoerpunten_profile", where)
        # check for intersects with layerForIntersects

        print (profileNumber)
    
        
        for theme, layer in layersForIntersects.items():
            if theme in klThemes:
                fieldsForIsect = isectFieldsKL
            else:
                fieldsForIsect = isectFields

            arcpy.analysis.Intersect([layer["name"],temp_profile], "temp_isects", "ALL", None, "POINT")

            isectCursor = arcpy.da.SearchCursor("temp_isects", fieldsForIsect)
            for isect in isectCursor:

                # get isect layer and join to nearest profile point
                isectNumber = int(isect[0])
                where = '"' + isectNumberField + '" = ' + str(isectNumber)
                temp_isect = "temp_isect"
                arcpy.Select_analysis("temp_isects", temp_isect, where)

                arcpy.analysis.SpatialJoin(temp_isect, "temp_uitvoerpunten_profile", "temp_isect_loc", "JOIN_ONE_TO_ONE", "KEEP_ALL", "", "CLOSEST", None, '')
                distanceValue = [cur[0] for cur in arcpy.da.SearchCursor("temp_isect_loc", "afstand")][0]
                subType = [cur[0] for cur in arcpy.da.SearchCursor("temp_isect_loc", subTypeField)][0]
                zValue = [cur[0] for cur in arcpy.da.SearchCursor("temp_isect_loc", "z_ahn")][0]

                if theme in klThemes:
                    diameterValue = [cur[0] for cur in arcpy.da.SearchCursor("temp_isect_loc", diameterField)][0]
                    pressureValue = [cur[0] for cur in arcpy.da.SearchCursor("temp_isect_loc", pressureField)][0]
                    materialValue = [cur[0] for cur in arcpy.da.SearchCursor("temp_isect_loc", materialField)][0]
                else:
                    diameterValue = None
                    pressureValue = None
                    materialValue = None

                if zValue == None:
                    zValue = 0
                isectTheme = isect[2]


                isectRow = {
                    'type': theme, 
                    'subtype':subType, 
                    'afstand': distanceValue, 
                    'hoogte' : isectPlotElevation,
                    'diameter': diameterValue,
                    'druk': pressureValue,
                    'materiaal': materialValue
                    
                    }
                isectDf = isectDf.append(isectRow, ignore_index=True)

    
        
        
        # create dataframe for plotting 
        profileArray = arcpy.da.FeatureClassToNumPyArray("temp_uitvoerpunten_profile", fieldsProfile, skip_nulls=True)
    

        df = pd.DataFrame(profileArray)
        dfProfile = df.sort_values('afstand', ascending=True)

        sheetName = "Profiel_{}".format(str(profileNumber))
        createProfileSheet(sheetName, dfProfile, isectDf)
       
    



else:
    copy_trajectory_lr(trajectlijn,code,offsetTrajectory)
    set_measurements_trajectory(profielen,trajectlijn,code,stapgrootte_punten)
    extract_z_arcpy(invoerpunten, uitvoerpunten, raster)
    add_xy(uitvoerpunten,code,trajectlijn)




