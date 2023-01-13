import arcpy
import sys
sys.path.append('.')

import pandas as pd
from xlsxwriter.workbook import Workbook
import matplotlib.colors as mcolors



arcpy.env.overwriteOutput = True
arcpy.env.workspace = r'D:\Projecten\WSRL\sterreschans_heteren\percelen_erfpacht\data.gdb'

excel = r'D:\Projecten\WSRL\sterreschans_heteren\percelen_erfpacht\percelen_buitendijks_pachters_filter.xlsx'

percelen = "percelen_zakelijk_recht_buitendijks_totaal"
velden = ["KADTOTAAL","ZR_OMSCHRIJVING","NAAM","VOORN","VOORL","VOORV","TITEL","STRAAT","HUISNR","POSTCODE","WOONPLAATS"]
velden_eigenaren = ["ZR_OMSCHRIJVING","NAAM","VOORN","VOORL","VOORV","TITEL","STRAAT","HUISNR","POSTCODE","WOONPLAATS"]
array = arcpy.da.FeatureClassToNumPyArray(percelen, velden)
df = pd.DataFrame(array)

# sorteren

df["volgorde"] = ""
df["Soorten pachters"] = ""

for index, row in df.iterrows():
    if row['ZR_OMSCHRIJVING'] == "Eigendom (recht van)":
        row["volgorde"] = 0

    elif "Erfpacht" in row['ZR_OMSCHRIJVING']:
          row["volgorde"] = 1

    else:
        row["volgorde"] = 2

df = df.sort_values(by=['volgorde'])


# df_selected = df[(df["ZR_OMSCHRIJVING"] == "Eigendom (recht van)") | (df["ZR_OMSCHRIJVING"] == "Erfpacht (recht van)") |(df["ZR_OMSCHRIJVING"] == "Erfpacht en Opstal (recht van)")]
df_selected = df




# opbouw xlsx
workbook = Workbook(excel)
worksheet = workbook.add_worksheet()

# stijl toevoegen voor headers
bold = workbook.add_format({'bold': True})
bold.set_bg_color("#25A4C6")
colors = list(mcolors.cnames.values())



# schrijf default kolomnamen
worksheet.write(0, 0, "Perceelnummer", bold)
worksheet.write(0, 1, "Aantal eigenaren/pachters", bold)
worksheet.write(0, 2, "Soorten pachters", bold)




# sorteer op perceelnummer (KADTOTAAL)
groep_percelen = df_selected.groupby('KADTOTAAL')

rijnummer = 1

for name, groep in groep_percelen:

    # erfpachters = False

    

    # check of erpachters aanwezig, anders skippen
    # for index, row in groep.iterrows():
    #     if "Erfpacht" in row["ZR_OMSCHRIJVING"]:
    #         erfpachters = True

    # check of pachters aanwezig, anders skippen

    pachters = False
    pachter_values = ["Erfpacht","Gebruik","Opstal","Zakelijk"]
    pachter_list = []


    for index, row in groep.iterrows():
        for item in pachter_values:
            if item in row["ZR_OMSCHRIJVING"]:
                if item in pachter_list:
                    pass
                else:
                    pachter_list.append(item)
                
                pachters = True

    
    pachter_list_string = [str(i) for i in pachter_list]
    pachter_list_string = ','.join(pachter_list_string)

    
    # if erfpachters == True:
    if pachters == True:
        kolomnummer = 3

        # per perceel een nieuwe rij aanmaken
        worksheet.write(rijnummer, 0, name)
        

        # per rij aantal erfpachters weergeven in kolom
        groupmembers = 0
        for index, row in groep.iterrows():
        
            groupmembers += 1
            


            # write extra header
            for veld in velden_eigenaren:
                

                if row[veld] == "None":
                    fill_value = ''
                else:
                    fill_value = row[veld]
                

            
                worksheet.write(0, kolomnummer, "{} {}".format(veld, groupmembers), bold)
                worksheet.write(rijnummer, kolomnummer, fill_value)

                kolomnummer += 1

        worksheet.write(rijnummer, 1, groupmembers)
        worksheet.write(rijnummer, 2, pachter_list_string)


        rijnummer += 1
    else:
        pass

        

workbook.close()








