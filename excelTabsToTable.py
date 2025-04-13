import openpyxl
import arcpy
import os

arcpy.env.overwriteOutput = True
arcpy.env.workspace = r"C:\Users\vince\Mijn Drive\WSRL\Boorpalen KIS 2024\temp.gdb"

excel_file = r"C:\Users\vince\Mijn Drive\WSRL\Boorpalen KIS 2024\inputdata\DKM_correctedXYZ.xlsx"
workbook = openpyxl.load_workbook(excel_file)

sheet_names = workbook.sheetnames
to_be_merged = []
merged_output = "cpt_table_merged"
total_points = "cpt_table_merged_fc"

for sheet_name in sheet_names:

    print(sheet_name)

    sheet = workbook[sheet_name]
    output_table = f"{sheet_name.replace('-','_')}_cpt_table"

    arcpy.ExcelToTable_conversion(excel_file, output_table, sheet_name)

    arcpy.management.CalculateField(
        in_table=output_table,
        field="cpt_id",
        expression=f"'{sheet_name}'",
        expression_type="PYTHON3",
        code_block="",
        field_type="TEXT",
        enforce_domains="NO_ENFORCE_DOMAINS"
    )

    to_be_merged.append(output_table)


    
workbook.close()

arcpy.management.Merge(
    inputs=to_be_merged,
    output= merged_output,
)

# table to featureclass
arcpy.management.XYTableToPoint(
    in_table="cpt_table_merged",
    out_feature_class=total_points,
    x_field="X_cor",
    y_field="Y_cor",
    z_field="mNAP",
    coordinate_system='PROJCS["RD_New",GEOGCS["GCS_Amersfoort",DATUM["D_Amersfoort",SPHEROID["Bessel_1841",6377397.155,299.1528128]],PRIMEM["Greenwich",0.0],UNIT["Degree",0.0174532925199433]],PROJECTION["Double_Stereographic"],PARAMETER["False_Easting",155000.0],PARAMETER["False_Northing",463000.0],PARAMETER["Central_Meridian",5.38763888888889],PARAMETER["Scale_Factor",0.9999079],PARAMETER["Latitude_Of_Origin",52.15616055555555],UNIT["Meter",1.0]];-30515500 -30279500 10000;-100000 10000;-100000 10000;0.001;0.001;0.001;IsHighPrecision'
)

arcpy.management.Copy(
    in_data=total_points,
    out_data=f"C:/Users/vince/Mijn Drive/WSRL/Boorpalen KIS 2024/Boorpalen KIS 2024.gdb/{total_points}",
)

# get max values for labels

