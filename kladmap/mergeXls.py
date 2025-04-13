# import pandas as pd

# # Read the Excel file
# excel_file = r"C:\Users\vince\Desktop\safe_pb\80263-2_Grondwatermonitoring_20230522.xlsx"
# sheets = pd.read_excel(excel_file, sheet_name=None)

# # Concatenate all sheets into one DataFrame
# combined_data = pd.concat(sheets.values(), ignore_index=True)

# # Write the combined data to a new Excel file
# combined_data.to_excel(r"C:\Users\vince\Desktop\safe_pb\80263-2_Grondwatermonitoring_20230522_combined.xlsx", index=False)





# import arcpy
# import os
# import arcpy.management
# import pandas as pd
# import unicodedata

# # Set the workspace environment
# arcpy.env.workspace = r"C:\Users\vince\Mijn Drive\WSRL\safe_data\safe_data\safe_data.gdb"
# arcpy.env.overwriteOutput = True

# # Input Excel file
# excel_file = r"C:\Users\vince\Desktop\safe_pb\80263-2_Grondwatermonitoring_20230522_totaal.xlsx"
# # Create an ExcelFile object
# xls = pd.ExcelFile(excel_file)

# # Get sheet names
# sheet_names = xls.sheet_names

# output_table = "safe_pb_17052024"

# # Create an empty list to hold all field names
# field_names = []
# tables = []
# index = 0

# # Iterate through each sheet in the Excel file
# for sheet_name in sheet_names:
#     # Generate a unique temporary table name for each sheet
#     temp_table = os.path.join(arcpy.env.workspace, "TempTable_" + str(index))
    
#     # Convert each sheet to a temporary table
#     arcpy.ExcelToTable_conversion(excel_file, temp_table, sheet_name)
    
#     arcpy.AddField_management(temp_table, "location", "TEXT")
#     with arcpy.da.UpdateCursor(temp_table, ["location"]) as cursor:
#         for row in cursor:
#             row[0] = sheet_name
#             cursor.updateRow(row)
        
#     # Append data to the output table
#     tables.append(temp_table)
    
#     index+=1

#     print (sheet_name, "done...")
    
#     # Delete the temporary table
#     # arcpy.Delete_management(temp_table)

# arcpy.management.Merge(tables, output_table)

# print("All sheets combined into one table successfully.")


import pandas as pd

# Load the Excel file
excel_file =  r"C:\Users\vince\Desktop\safe_pb\80263-2_Grondwatermonitoring_20230522_totaal.xlsx"
output_mergd = r"C:\Users\vince\Desktop\safe_pb\merged_26062024.xlsx"
# Load all sheet names
sheet_names = pd.ExcelFile(excel_file).sheet_names

# Initialize an empty list to hold DataFrames
dfs = []

# Loop through each sheet name and read it into a DataFrame
for sheet in sheet_names:
    df = pd.read_excel(excel_file, sheet_name=sheet)
    dfs.append(df)

# Concatenate all DataFrames
merged_df = pd.concat(dfs, ignore_index=True)

# Save the merged DataFrame to a new Excel file
merged_df.to_excel('merged_output.xlsx', index=False)