
import arcpy
arcpy.env.overwriteOutput = True
arcpy.env.workspace = r"C:\Users\vince\Mijn Drive\WSRL\hwbp innovaties 2023\kaart_inladen\kaart_inladen.gdb"

input_segments = "projectdefinities_wvp_v2"
input_categories = r"C:\Users\vince\Mijn Drive\WSRL\hwbp innovaties 2023\kaart_inladen\inputdata\LBO1\resultaten_LBO1.gdb\Totaal_resultaat_LBO1_v1"
temp_category_layer = "temp_categories_split_singlepart"
# stbi_oordeel = "lbo_split_single_join_projectdef"
# stph_oordeel = "lbo_split_single_join_projectdef"
stbi_field = "STBI"
stph_field = "STPH"
id_field = "project_id"

categories_sufficient = ["Iv","IIv","IIIv","-"]
categories_insufficient = ["IVv","Vv","VIv"]

output_segments = "projectdefinities_wvp_v2_oordeel_v2"

# copy feature
arcpy.management.CopyFeatures(input_segments, output_segments)

# create start+endpoints
arcpy.management.FeatureVerticesToPoints(
    in_features=input_segments,
    out_feature_class="temp_splitpoints",
    point_location="BOTH_ENDS"
)

arcpy.management.SplitLineAtPoint(
    in_features=input_categories,
    point_features="temp_splitpoints",
    out_feature_class="temp_categories_split_multipart",
    search_radius="0.5 Meters"
)

arcpy.management.MultipartToSinglepart(
    in_features="temp_categories_split_multipart",
    out_feature_class="temp_categories_singlepart"
)

arcpy.analysis.SpatialJoin(
    target_features="temp_categories_singlepart",
    join_features=input_segments,
    out_feature_class=temp_category_layer,
    join_operation="JOIN_ONE_TO_ONE",
    join_type="KEEP_ALL",
    match_option="SHARE_A_LINE_SEGMENT_WITH",
    search_radius=None,
    distance_field_name=""
)


# add fields
arcpy.AddField_management(output_segments, "stph_stbi_voldoende" , "DOUBLE", 2, field_is_nullable="NULLABLE")
arcpy.AddField_management(output_segments, "stph_stbi_onvoldoende" , "DOUBLE", 2, field_is_nullable="NULLABLE")
arcpy.AddField_management(output_segments, "stbi_voldoende_stph_onvoldoende" , "DOUBLE", 2, field_is_nullable="NULLABLE")
arcpy.AddField_management(output_segments, "stbi_onvoldoende_stph_voldoende" , "DOUBLE", 2, field_is_nullable="NULLABLE")
arcpy.AddField_management(output_segments, "berekende_lengte" , "DOUBLE", 2, field_is_nullable="NULLABLE")


# iterate over segments
segment_cursor = arcpy.da.UpdateCursor(output_segments, [
    "project_id",
    "stph_stbi_voldoende",
    "stph_stbi_onvoldoende",
    "stbi_voldoende_stph_onvoldoende",
    "stbi_onvoldoende_stph_voldoende",
    "berekende_lengte"
])

for row in segment_cursor:
    project_id = row[0]
    print (project_id)

    stph_stbi_voldoende_m = 0
    stph_stbi_onvoldoende_m = 0
    stbi_voldoende_stph_onvoldoende_m = 0
    stbi_onvoldoende_stph_voldoende_m = 0
    berekende_lengte_m = 0

    
    # stph+stbi part
    temp_oordeel_layer = arcpy.MakeFeatureLayer_management(temp_category_layer, "templayer") 
    arcpy.management.SelectLayerByAttribute(
        in_layer_or_view="templayer",
        selection_type="NEW_SELECTION",
        where_clause="{} = '{}'".format(id_field,project_id),
        invert_where_clause=None
    )
    
    o_cur = arcpy.da.SearchCursor(temp_oordeel_layer, [[stph_field, stbi_field],"SHAPE@LENGTH"])
    for o_row in o_cur:


        category_stph = o_row[0]
        category_stbi = o_row[1]
        length = o_row[2]


        if category_stph in categories_sufficient and category_stbi in categories_sufficient:
            stph_stbi_voldoende_m += length
            berekende_lengte_m += length

        elif category_stph in categories_insufficient and category_stbi in categories_insufficient:
            stph_stbi_onvoldoende_m += length
            berekende_lengte_m += length

        elif category_stbi in categories_sufficient and category_stph in categories_insufficient:
            stbi_voldoende_stph_onvoldoende_m += length
            berekende_lengte_m += length

        elif category_stbi in categories_insufficient and category_stph in categories_sufficient:
            stbi_onvoldoende_stph_voldoende_m += length
            berekende_lengte_m += length
        

        
    row[1] = stph_stbi_voldoende_m
    row[2] = stph_stbi_onvoldoende_m
    row[3] = stbi_voldoende_stph_onvoldoende_m
    row[4] = stbi_onvoldoende_stph_voldoende_m
    row[5] = berekende_lengte_m

    segment_cursor.updateRow(row)

arcpy.management.CalculateField(
    in_table=output_segments,
    field="Trajectlengte",
    expression="Length($feature)",
    expression_type="ARCADE",
    code_block="",
    field_type="TEXT",
    enforce_domains="NO_ENFORCE_DOMAINS"
)

