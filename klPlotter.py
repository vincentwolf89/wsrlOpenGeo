# generate profiles or get profile input
from xlsxwriter.workbook import Workbook


import arcpy
from base import *

arcpy.env.overwriteOutput = True
arcpy.env.workspace = r"C:\Users\vince\Mijn Drive\WSRL\kabels en leidingen ssh\test.gdb"

offsetTrajectory = 10
newProfiles = True
trajectlijn = "deeltraject_c_testsectie"
profielen = "profielen_{}".format(trajectlijn)
# profielen = "profielen_deeltraject_c_testsectie_joost"

butlijn = "butlijn_ssh"
buklijn = "buklijn_ssh"
biklijn = "biklijn_ssh"
bitlijn = "bitlijn_ssh"
riverpoly = "temp_riverpoly"


profiel_interval = 500
profiel_lengte_land = 800
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

isectDfColumns = ["type","afstand","hoogte","diameter","druk","materiaal","breedte_kruin","hoogte_dijk","krater_straal","krater_diepte","xl","x_bit","x_but"]
elevationSourceName = "AHN3"
fieldsProfile = ["profielnummer","afstand","z_ahn","x","y"]
plotLocation= "C:/Users/vince/Mijn Drive/WSRL/kabels en leidingen ssh/output/xlsx_joost_19102023/"
isectPlotElevation = 4

# outputvariables for toetsing
defaultDikeHeight = 5
faalkansenTable = r"C:\Users\vince\Mijn Drive\WSRL\kabels en leidingen ssh\aanlevering\toetsingtabellen\toetstabel_kl_deltares_03102023.xlsx"
lfSheetWater = "lf_drinkwater"
lfSheetGas = "lf_gas"
krSheetWater = "kr_drinkwater"
krSheetGas = "kr_gas"
defaultDiameter = 100 # change this!
defaultPressure = 0.1
defaultMaterial = "Staal"
materialFieldLfTable = "Materiaal"
kraterDiepteColumn = "kraterdiepte"




klThemes = ["riool","water","ogc"]
refThemes = ["buitenteen","buitenkruin","binnenkruin","binnenteen"]

layersForIntersects = {
    "buitenteen": {
        "type":"ref",
        "name":butlijn,
        "symbol":"square",
    },
    "buitenkruin": {
        "type":"ref",
        "name":buklijn,
        "symbol":"square",
    },
    "binnenkruin": {
        "type":"ref",
        "name":biklijn,
        "symbol":"square",
    },
    "binnenteen": {
        "type":"ref",
        "name":bitlijn,
        "symbol":"square",
    },
    "riool": {
        "type":"kl",
        "name":"merge_r_rd",
        "symbol":"circle",
    },
    "water": {
        "type":"kl",
        "name":"merge_w_rd",
        "symbol":"circle",
    },
    "ogc": {
        "type":"kl",
        "name":"merge_ogc_rd",
        "symbol":"circle",
    },
}

colorsForIntersects = {
  "rioolVrijverval": "#F64222",
  "rioolOnderOverOfOnderdruk":"#C72205",
  "water": "#2232F6",
  "buisleidingGevaarlijkeInhoud":"#DCCA11",
  "gasHogeDruk":"#0066B2",
  "gasLageDruk":"#25A3FF",
  "buitenkruin":"#C1781F",
  "binnenkruin":"#EA5611",
  "binnenteen":"#148809",
  "buitenteen":"#1E47C6",
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

    worksheet1.write(0, 6, "Type", bold)
    worksheet1.write(0, 7, "Subtype", bold)
    worksheet1.write(0, 8, "Afstand", bold)
    worksheet1.write(0, 9, "Hoogte", bold)
    worksheet1.write(0, 10, "Diameter", bold)
    worksheet1.write(0, 11, "Druk", bold)
    worksheet1.write(0, 12, "Materiaal", bold)

    worksheet1.write(0, 14, "Breedte kruin", bold)
    worksheet1.write(0, 15, "Hoogte dijk", bold)
    worksheet1.write(0, 16, "Breedte berm", bold)
    worksheet1.write(0, 17, "Dikte deklaag", bold)

    worksheet1.write(0, 18, "xL (t.o.v. rivier)", bold)
    worksheet1.write(0, 19, "xBut (t.o.v. rivier)", bold)
    worksheet1.write(0, 20, "xBit (t.o.v. rivier)", bold)
    worksheet1.write(0, 21, "Binnenteen naar berm (Xlb)", bold)
    worksheet1.write(0, 22, "Type dijk", bold)
    worksheet1.write(0, 23, "Kraterstraal (R)", bold)
    worksheet1.write(0, 24, "Kraterdiepte", bold)

    worksheet1.write(0, 25, "C1A", bold)
    worksheet1.write(0, 26, "C1B", bold)
    worksheet1.write(0, 27, "C2A", bold)
    worksheet1.write(0, 28, "C2B", bold)
    worksheet1.write(0, 29, "C2C", bold)
    worksheet1.write(0, 30, "C2D", bold)
    worksheet1.write(0, 31, "C3", bold)
    worksheet1.write(0, 32, "C4", bold)
    worksheet1.write(0, 33, "Afstand leiding tot dijk", bold)
    





    # write colums
    worksheet1.write_column('A2', profilePoints['profielnummer'])
    worksheet1.write_column('B2', profilePoints['afstand'])
    worksheet1.write_column('C2', profilePoints['z_ahn'])
    worksheet1.write_column('D2', profilePoints['x'])
    worksheet1.write_column('E2', profilePoints['y'])

    worksheet1.write_column('G2', isectPoints['type'])
    worksheet1.write_column('H2', isectPoints['subtype'])
    worksheet1.write_column('I2', isectPoints['afstand'])
    worksheet1.write_column('J2', isectPoints['hoogte'])
    worksheet1.write_column('K2', isectPoints['diameter'])
    worksheet1.write_column('L2', isectPoints['druk'])
    worksheet1.write_column('M2', isectPoints['materiaal'])



    worksheet1.write_column('O2', isectPoints['breedte_kruin'])
    worksheet1.write_column('P2', isectPoints['hoogte_dijk'])

    worksheet1.write_column('S2', isectPoints['xl'])
    worksheet1.write_column('T2', isectPoints['x_but'])
    worksheet1.write_column('U2', isectPoints['x_bit'])


    worksheet1.write_column('X2', isectPoints['krater_straal'])
    worksheet1.write_column('Y2', isectPoints['krater_diepte'])
    # worksheet1.write_column('R2', isectPoints['materiaal'])
    # worksheet1.write_column('S2', isectPoints['materiaal'])
    # worksheet1.write_column('T2', isectPoints['materiaal'])

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
            'categories': '=Overzicht!$I${}:$I${}'.format(rowIndex,rowIndex),
            'values':     '=Overzicht!$J${}:$J${}'.format(rowIndex,rowIndex),
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

def createProfileData(profielen, profileFields):
    
    # create df for toetsingstabellen
    df_lf_water = pd.read_excel(faalkansenTable, sheet_name=lfSheetWater)
    df_lf_gas = pd.read_excel(faalkansenTable, sheet_name=lfSheetGas)

    df_kr_water =pd.read_excel(faalkansenTable, sheet_name=krSheetWater)
    df_kr_gas = pd.read_excel(faalkansenTable, sheet_name=krSheetGas)


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

        # create dataframe for plotting 
        profileArray = arcpy.da.FeatureClassToNumPyArray("temp_uitvoerpunten_profile", fieldsProfile, skip_nulls=True)
        dfProfile = pd.DataFrame(profileArray)
        dfProfileSorted = dfProfile.sort_values('afstand', ascending=True)
        riverBorderX =  dfProfileSorted['afstand'].max()
        
        # check for intersects with layerForIntersects
        print (profileNumber)
    
        # first do ref part
        refDict = {theme: layer for theme, layer in layersForIntersects.items() if theme in refThemes}
        klDict = {theme: layer for theme, layer in layersForIntersects.items() if theme in klThemes}
        for theme, layer in refDict.items():
   
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


                if zValue == None:
                    zValue = isectPlotElevation
                isectTheme = isect[2]


                # calc xL
                xL = abs(riverBorderX - distanceValue)

                isectRow = {
                    'type': theme, 
                    'subtype':subType, 
                    'afstand': distanceValue, 
                    'hoogte' : zValue,
                    'diameter': "",
                    'druk': "",
                    'materiaal': "",
                    'breedte_kruin' : "",
                    'hoogte_dijk' : "",
                    'krater_straal': "",
                    'krater_diepte': "",
                    'xl': xL,
                    'x_bit': "",
                    'x_but': "",
                }
                
                isectRow_df = pd.DataFrame([isectRow])
                isectDf = pd.concat([isectDf, isectRow_df], ignore_index=True)

        

        # calc geom data if possible
        z_bik = isectDf.loc[isectDf['type'] == 'binnenkruin', 'hoogte'].values[0] 
        z_buk = isectDf.loc[isectDf['type'] == 'buitenkruin', 'hoogte'].values[0] 
        z_bit = isectDf.loc[isectDf['type'] == 'binnenteen', 'hoogte'].values[0] 
        z_but = isectDf.loc[isectDf['type'] == 'buitenteen', 'hoogte'].values[0]

        a_bik = isectDf.loc[isectDf['type'] == 'binnenkruin', 'afstand'].values[0] 
        a_buk = isectDf.loc[isectDf['type'] == 'buitenkruin', 'afstand'].values[0] 
        a_bit = isectDf.loc[isectDf['type'] == 'binnenteen', 'afstand'].values[0] 
        a_but = isectDf.loc[isectDf['type'] == 'buitenteen', 'afstand'].values[0]


        base_elevation = calculate_absolute_difference(z_bit, z_but)
        top_elevation = calculate_absolute_difference(z_bik, z_buk)
        if base_elevation is None or top_elevation is None: 
            dike_height = defaultDikeHeight
        else:
            dike_height = round(abs(base_elevation-top_elevation),2)

        crest_width = round(abs(isectDf.loc[isectDf['type'] == 'binnenkruin', 'afstand'].values[0] -isectDf.loc[isectDf['type'] == 'buitenkruin', 'afstand'].values[0]),2)
        
        
  

        # after that kl part
        for theme, layer in klDict.items():
   
            fieldsForIsect = isectFieldsKL
      
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

                diameterValue = [cur[0] for cur in arcpy.da.SearchCursor("temp_isect_loc", diameterField)][0]
                pressureValue = [cur[0] for cur in arcpy.da.SearchCursor("temp_isect_loc", pressureField)][0]
                materialValue = [cur[0] for cur in arcpy.da.SearchCursor("temp_isect_loc", materialField)][0]

                # find kraterstraal, kraterdiepte, set defaults --> work needed
                if diameterValue is None or diameterValue =="":
                    lookupDiameter = defaultDiameter
                else:
                    lookupDiameter = float(defaultDiameter) 

                if pressureValue is None or pressureValue =="":
                    lookupPressure = defaultPressure
                else:
                    lookupPressure = float(pressureValue)

                if materialValue is None or materialValue =="":
                    lookupMaterial = defaultMaterial


                # find kraterstraal, kraterdiepte
                kraterStraal = ""
                kraterDiepte = ""
                if theme =="water" or theme == "ogc":
                    if theme == "water":
                        df_krater = df_kr_water
                    if theme == "ogc":
                        df_krater = df_kr_gas
                    
                    try:
                        rangeDiameter = None
                        for val in df_krater[df_krater.columns[0]]:
                            if "-" in val:
                                lower, upper = map(float, val.split('-'))
                                # print (lower,upper, lookupDiameter)
                                if lower <=lookupDiameter <= upper:
                                    rangeDiameter = val
                                    break
                        
                        rangePressure = None
                        for col in df_krater.columns:
                            if "-" in col:
                                lower, upper = map(float, col.split('-'))
                                if lower <= lookupPressure <= upper:
                                    rangePressure = col
                                    break
         
            
                        kraterStraal= df_krater.loc[df_krater['range'] == rangeDiameter, rangePressure].values[0]
                        kraterDiepte =  df_krater.loc[df_krater['range'] == rangeDiameter, kraterDiepteColumn].values[0]
                        
             

                        
                        print (rangeDiameter, rangePressure, kraterStraal, kraterDiepte)
                    except Exception as e:
                        print (e, rangeDiameter, rangePressure)




                if zValue == None:
                    zValue = isectPlotElevation
                isectTheme = isect[2]


                # calc xL, xBit, xBut
                xL = abs(riverBorderX - distanceValue)
                xBit = abs(riverBorderX - a_bit)
                xBut = abs(riverBorderX - a_but)

                print (riverBorderX, xL, "test!! geom")

                isectRow = {
                    'type': theme, 
                    'subtype':subType, 
                    'afstand': distanceValue, 
                    'hoogte' : zValue,
                    'diameter': diameterValue,
                    'druk': pressureValue,
                    'materiaal': materialValue,
                    'breedte_kruin' : crest_width,
                    'hoogte_dijk' : dike_height,
                    'krater_straal': kraterStraal,
                    'krater_diepte': kraterDiepte,
                    'xl': xL,
                    'x_bit': xBit,
                    'x_but': xBut,
                    }
                
                isectRow_df = pd.DataFrame([isectRow])
                isectDf = pd.concat([isectDf, isectRow_df], ignore_index=True)
       

    

        sheetName = "Profiel_{}".format(str(profileNumber))
        createProfileSheet(sheetName, dfProfileSorted, isectDf)




if newProfiles is True:
    # copy_trajectory_lr(trajectlijn,code,offsetTrajectory)
    # generate_profiles(profiel_interval,profiel_lengte_land,profiel_lengte_rivier,trajectlijn,code,profielen)

    # # cut profiles on riverpoly
    # arcpy.analysis.Erase(
    #     in_features=profielen,
    #     erase_features=riverpoly,
    #     out_feature_class= "temp_profiles_erased",
    #     cluster_tolerance=None
    # )
    # arcpy.management.CopyFeatures("temp_profiles_erased", profielen)

    # set_measurements_trajectory(profielen,trajectlijn,code,stapgrootte_punten)
    # extract_z_arcpy(invoerpunten, uitvoerpunten, raster)
    # add_xy(uitvoerpunten,code,trajectlijn)
    createProfileData(profielen, profileFields)

    

    
       
    



else:
    # copy_trajectory_lr(trajectlijn,code,offsetTrajectory)
    # set_measurements_trajectory(profielen,trajectlijn,code,stapgrootte_punten)
    # extract_z_arcpy(invoerpunten, uitvoerpunten, raster)
    # add_xy(uitvoerpunten,code,trajectlijn)
    createProfileData(profielen, profileFields)













