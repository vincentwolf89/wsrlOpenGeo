
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

categories_sufficient = ["Iv","IIv"]
categories_mid = ["IIIv"]
categories_insufficient = ["IVv","Vv","VIv"]

output_segments = "projectdefinities_wvp_v2_oordeel"

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
arcpy.AddField_management(output_segments, "stbi_voldoende" , "DOUBLE", 2, field_is_nullable="NULLABLE")
arcpy.AddField_management(output_segments, "stbi_midden" , "DOUBLE", 2, field_is_nullable="NULLABLE")
arcpy.AddField_management(output_segments, "stbi_onvoldoende" , "DOUBLE", 2, field_is_nullable="NULLABLE")

arcpy.AddField_management(output_segments, "stph_voldoende" , "DOUBLE", 2, field_is_nullable="NULLABLE")
arcpy.AddField_management(output_segments, "stph_midden" , "DOUBLE", 2, field_is_nullable="NULLABLE")
arcpy.AddField_management(output_segments, "stph_onvoldoende" , "DOUBLE", 2, field_is_nullable="NULLABLE")


# iterate over segments
segment_cursor = arcpy.da.UpdateCursor(output_segments, ["project_id","stbi_voldoende","stbi_midden","stbi_onvoldoende","stph_voldoende","stph_midden","stph_onvoldoende"])
for row in segment_cursor:
    project_id = row[0]
    print (project_id)

    stbi_sufficient_m = 0
    stbi_mid_m = 0
    stbi_insufficient_m = 0
    stph_sufficient_m = 0
    stph_mid_m = 0
    stph_insufficient_m = 0

    # stbi part
    temp_stbi = arcpy.MakeFeatureLayer_management(temp_category_layer, "templayer") 
    arcpy.management.SelectLayerByAttribute(
        in_layer_or_view="templayer",
        selection_type="NEW_SELECTION",
        where_clause="{} = '{}'".format(id_field,project_id),
        invert_where_clause=None
    )
    
    stbi_cursor = arcpy.da.SearchCursor(temp_stbi, [stbi_field,"SHAPE@LENGTH"])
    for stbi_row in stbi_cursor:
        category = stbi_row[0]
        length = stbi_row[1]

        if category in categories_sufficient:
            stbi_sufficient_m += length
        
        if category in categories_mid:
            stbi_mid_m += length

        if category in categories_insufficient:
            stbi_insufficient_m += length
        
    row[1] = stbi_sufficient_m
    row[2] = stbi_mid_m
    row[3] = stbi_insufficient_m

    # stph part
    temp_stph = arcpy.MakeFeatureLayer_management(temp_category_layer, "templayer") 
    arcpy.management.SelectLayerByAttribute(
        in_layer_or_view="templayer",
        selection_type="NEW_SELECTION",
        where_clause="{} = '{}'".format(id_field,project_id),
        invert_where_clause=None
    )
    
    stph_cursor = arcpy.da.SearchCursor(temp_stph, [stph_field,"SHAPE@LENGTH"])
    for stph_row in stph_cursor:
        category = stph_row[0]
        length = stph_row[1]

        if category in categories_sufficient:
            stph_sufficient_m += length
        
        if category in categories_mid:
            stph_mid_m += length

        if category in categories_insufficient:
            stph_insufficient_m += length
        
    row[4] = stph_sufficient_m
    row[5] = stph_mid_m
    row[6] = stph_insufficient_m

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

