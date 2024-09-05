import arcpy
arcpy.env.overwriteOutput = True
from arcpy.sa import *
import pandas as pd
import matplotlib.pyplot as plt
import gc
from collections import OrderedDict

arcpy.env.workspace = r"C:\Users\vince\Mijn Drive\WSRL\safe_lengteprofielen_072024\safe_lengteprofielen_072024.gdb"

# inputs
input_trajects = "testvakken_dz11"
input_dijkpalen = "dijkpalen_safe_rd"
input_houses = "drempelhoogtes_05092024"
ahn4_raster = "safe_ahn4_buffer_200m"
raster_1 = "temp_tin_raster_clip"
dijkvak_field = "Vaknaam"
dijkpaal_field = "rftident"
point_loc_field = "point_loc"
dp_loc_field = "dp_loc"
houses_loc_field = "house_loc"
plotdir = "C:/Users/vince/Mijn Drive/WSRL/safe_lengteprofielen_072024/outputs/"

# fields
ahn4_field = "ahn4"
raster_1_field = "raster1"
houses_field = "drempelhoogte"

# names
ahn4_name = "AHN4-DTM 0.50m"
raster_1_name = "VKA 08-2024"


point_distance = 1 # m 

# werkdata
point_layer = "temp_pointlayer"
dijkpaal_layer = "temp_dijkpalen_traject"
houses_layer = "temp_drempelhoogtes_temp"




def part1(input_traject):
    # generate points over lines
    arcpy.management.GeneratePointsAlongLines(
        Input_Features=input_traject,
        Output_Feature_Class=point_layer,
        Point_Placement="DISTANCE",
        Distance=f"{point_distance} Meters",
        Percentage=None,
        Include_End_Points="END_POINTS",
        Add_Chainage_Fields="ADD_CHAINAGE"
    )

    print ("points generated")


    # extract values for points for all rasters
    arcpy.sa.ExtractMultiValuesToPoints(
        in_point_features=point_layer,
        in_rasters=f"{ahn4_raster} {ahn4_field};{raster_1} {raster_1_field}",
        bilinear_interpolate_values="NONE"
    )


    print ("values extracted")

    # locate dijkpalen along points

    arcpy.management.AddFields(
        in_table=input_traject,
        field_description="van DOUBLE # # # #;tot DOUBLE # # # #",
        template=None
    )

    arcpy.management.CalculateFields(
        in_table=input_traject,
        expression_type="PYTHON3",
        fields="van 0 #;tot round(!Shape_Length!) #",
        code_block="",
        enforce_domains="NO_ENFORCE_DOMAINS"
    )

    arcpy.lr.CreateRoutes(
        in_line_features=input_traject,
        route_id_field=dijkvak_field,
        out_feature_class="temp_routes",
        measure_source="TWO_FIELDS",
        from_measure_field="van",	
        to_measure_field="tot",
        coordinate_priority="UPPER_LEFT",
        measure_factor=1,
        measure_offset=0,
        ignore_gaps="IGNORE",
        build_index="INDEX"
    )
    print ("routes created")

    # join dijkpalen to trajectlijn
    arcpy.analysis.SpatialJoin(
        target_features=input_dijkpalen,
        join_features=input_traject,
        out_feature_class=dijkpaal_layer,
        join_operation="JOIN_ONE_TO_ONE",
        join_type="KEEP_ALL",
        match_option="CLOSEST",
        search_radius=None,
        distance_field_name="",
        match_fields=None
    )

    arcpy.lr.LocateFeaturesAlongRoutes(
        in_features=dijkpaal_layer,
        in_routes="temp_routes",
        route_id_field=dijkvak_field,
        radius_or_tolerance="50 Meters",
        out_table="temp_dijkpalen_table",
        out_event_properties="RID; POINT; dp_loc",
        route_locations="FIRST",
        distance_field="DISTANCE",
        zero_length_events="ZERO",
        in_fields="FIELDS",
        m_direction_offsetting="M_DIRECTON"
    )

    arcpy.management.JoinField(
        in_data=dijkpaal_layer,
        in_field=dijkpaal_field,
        join_table="temp_dijkpalen_table",
        join_field=dijkpaal_field,
        fields=dp_loc_field,
        fm_option="NOT_USE_FM",
        field_mapping=None,
        index_join_fields="NO_INDEXES"
    )


    print ("dijkpalen joined and located")

    # join drempelhoogtes to trajectlijn
    arcpy.analysis.SpatialJoin(
        target_features=input_houses,
        join_features=input_traject,
        out_feature_class=houses_layer,
        join_operation="JOIN_ONE_TO_ONE",
        join_type="KEEP_ALL",
        match_option="CLOSEST",
        search_radius=None,
        distance_field_name="",
        match_fields=None
    )

    arcpy.lr.LocateFeaturesAlongRoutes(
        in_features=houses_layer,
        in_routes="temp_routes",
        route_id_field=dijkvak_field,
        radius_or_tolerance="50 Meters",
        out_table="temp_houses_table",
        out_event_properties="RID; POINT; house_loc",
        route_locations="FIRST",
        distance_field="DISTANCE",
        zero_length_events="ZERO",
        in_fields="FIELDS",
        m_direction_offsetting="M_DIRECTON"
    )

    arcpy.management.JoinField(
        in_data=houses_layer,
        in_field=houses_field,
        join_table="temp_houses_table",
        join_field=houses_field,
        fields=houses_loc_field,
        fm_option="NOT_USE_FM",
        field_mapping=None,
        index_join_fields="NO_INDEXES"
    )

    print ("houses joined and located")

    arcpy.lr.LocateFeaturesAlongRoutes(
        in_features=point_layer,
        in_routes="temp_routes",
        route_id_field=dijkvak_field,
        radius_or_tolerance="50 Meters",
        out_table="temp_point_table",
        out_event_properties="RID; POINT; point_loc",
        route_locations="FIRST",
        distance_field="DISTANCE",
        zero_length_events="ZERO",
        in_fields="FIELDS",
        m_direction_offsetting="M_DIRECTON"
    )



    arcpy.management.JoinField(
        in_data=point_layer,
        in_field="ORIG_SEQ",
        join_table="temp_point_table",
        join_field="ORIG_SEQ",
        fields="point_loc",
        fm_option="NOT_USE_FM",
        field_mapping=None,
        index_join_fields="NO_INDEXES"
    )





def part2(name):
    point_array = arcpy.da.FeatureClassToNumPyArray(point_layer, [point_loc_field,ahn4_field,raster_1_field])
    dijkpaal_array = arcpy.da.FeatureClassToNumPyArray(dijkpaal_layer, [dp_loc_field, dijkpaal_field])
    houses_array = arcpy.da.FeatureClassToNumPyArray(houses_layer, [houses_loc_field, houses_field])
    df_point = pd.DataFrame(point_array)
    df_dijkpaal = pd.DataFrame(dijkpaal_array)
    df_houses = pd.DataFrame(houses_array)
    merged_df = pd.concat([df_point, df_dijkpaal, df_houses], ignore_index=True)
    merged_df = merged_df.sort_values([point_loc_field], ascending=[True])

    # set min and max based on df
    min_ahn_value = merged_df[ahn4_field].min()
    max_ahn_value = merged_df[ahn4_field].max()
    plt.ylim(min_ahn_value-2, max_ahn_value+2)


    fig = plt.figure(figsize=(50, 15))
    ax1 = fig.add_subplot(111, label ="1")
    ax1.grid(visible=True, which='major', color='grey', linewidth=1.0, alpha=0.2)

    # plot all rasters
    ax1.plot(merged_df[point_loc_field], merged_df[ahn4_field], color='red', label=ahn4_name, linewidth=3)
    ax1.plot(merged_df[point_loc_field], merged_df[raster_1_field], color='blue', label=raster_1_name, linewidth=3)
    
    for index, row in merged_df.iterrows():
        if pd.notna(row[dp_loc_field]):
            ax1.annotate(row[dijkpaal_field], (row[dp_loc_field], min_ahn_value -1), fontsize=20)
        
    # ax1.plot(merged_df[dp_loc_field], [2] * len(merged_df[dp_loc_field]), color='grey', label="Dijkpalen", marker = 'o')
    ax1.scatter(merged_df[dp_loc_field], [min_ahn_value -1] * len(merged_df[dp_loc_field]), color='grey', label="Dijkpalen", marker='o')
    ax1.scatter(merged_df[houses_loc_field], merged_df[houses_field], color='orange', label="Drempelhoogtes", marker='v', s=200)
    print (merged_df)
    # ax1.axhline(hoogte, color='blue', linestyle='-',linewidth=5,label=f"Leggerhoogte ({round(hoogte,1)} m NAP)")

    ax1.set_title(f'Lengteprofiel {name}', fontsize=30, x=0.5, y=0.95)

    ax1.tick_params(axis='both', which='major', labelsize=16)
    ax1.tick_params(axis='both', which='minor', labelsize=16)

    plt.tight_layout(pad=2)

    ax1.set_xlabel('Afstand [m]' ,fontsize=30)
    ax1.xaxis.set_label_coords(0.5, 0.03) 
    ax1.set_ylabel('Hoogte [m NAP]', fontsize=30)
    ax1.yaxis.set_label_coords(0.01, 0.5)

    handles, labels = plt.gca().get_legend_handles_labels()

    label_dict = OrderedDict() 
    for handle, label in zip(handles, labels):
        if label not in label_dict:
            label_dict[label] = handle

    legend = plt.legend(label_dict.values(), label_dict.keys(),loc='lower right',prop={'size': 20}, fancybox=True, framealpha=0.9)

    legend._legend_box.align = "left"


    plt.savefig(plotdir + f"profile_{name}.png")
    fig.clf()
    plt.close(fig)
    gc.collect()
    print (f"plot saved for dijkvak: {name}")



with arcpy.da.SearchCursor(input_trajects, [dijkvak_field]) as cursor:
    for row in cursor:
        name = row[0]

        input_traject = arcpy.MakeFeatureLayer_management(input_trajects, "flayer") 
        arcpy.management.SelectLayerByAttribute(
            in_layer_or_view="flayer",
            selection_type="NEW_SELECTION",
            where_clause=f"{dijkvak_field} = '{name}'",
            invert_where_clause=None
        )

        part1(input_traject)
        part2(name)



