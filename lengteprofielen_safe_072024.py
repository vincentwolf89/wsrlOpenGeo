import arcpy
arcpy.env.overwriteOutput = True
from arcpy.sa import *
import pandas as pd
import matplotlib.pyplot as plt
import gc
from collections import OrderedDict

arcpy.env.workspace = r"C:\Users\vince\Documents\ArcGIS\Projects\safe_lengteprofielen_072024\safe_lengteprofielen_072024.gdb"

# inputs
input_trajects = "testvak"
input_dijkpalen = "dijkpalen_safe_rd"
ahn4_raster = "https://tiles.arcgis.com/tiles/nSZVuSZjHpEZZbRo/arcgis/rest/services/Elevation_3D_RD/ImageServer"
raster_1 = r"C:\Users\vince\Documents\ArcGIS\Projects\safe ahn\safe ahn.gdb\safe_ahn4_200mbuffer"
dijkvak_field = "Vaknaam"
dijkpaal_field = "rftident"
point_loc_field = "point_loc"
dp_loc_field = "dp_loc"
plotdir = "C:/Users/vince/Documents/ArcGIS/Projects/safe_lengteprofielen_072024/outputs/"

# fields
ahn4_field = "ahn4"
raster_1_field = "raster1"

point_distance = 1 # m 

# werkdata
point_layer = "temp_pointlayer"
dijkpaal_layer = "temp_dijkpalen_traject"

def part1():
    # generate points over lines
    arcpy.management.GeneratePointsAlongLines(
        Input_Features=input_trajects,
        Output_Feature_Class=point_layer,
        Point_Placement="DISTANCE",
        Distance=f"{point_distance} Meters",
        Percentage=None,
        Include_End_Points="END_POINTS",
        Add_Chainage_Fields="ADD_CHAINAGE"
    )

    print ("points generated")


    # extract values for points
    arcpy.sa.ExtractMultiValuesToPoints(
        in_point_features=point_layer,
        in_rasters=f"{ahn4_raster} {ahn4_field};{ahn4_raster} {raster_1_field}",
        bilinear_interpolate_values="NONE"
    )

    print ("values extracted")

    # locate dijkpalen along points

    arcpy.management.AddFields(
        in_table=input_trajects,
        field_description="van DOUBLE # # # #;tot DOUBLE # # # #",
        template=None
    )

    arcpy.management.CalculateFields(
        in_table=input_trajects,
        expression_type="PYTHON3",
        fields="van 0 #;tot round(!Shape_Length!) #",
        code_block="",
        enforce_domains="NO_ENFORCE_DOMAINS"
    )

    arcpy.lr.CreateRoutes(
        in_line_features=input_trajects,
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
        join_features=input_trajects,
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


# part1()

point_array = arcpy.da.FeatureClassToNumPyArray(point_layer, [point_loc_field,ahn4_field,raster_1_field])
dijkpaal_array = arcpy.da.FeatureClassToNumPyArray(dijkpaal_layer, [dp_loc_field, dijkpaal_field])
df_point = pd.DataFrame(point_array)
df_dijkpaal = pd.DataFrame(dijkpaal_array)
merged_df = pd.concat([df_point, df_dijkpaal], ignore_index=True)

# print (merged_df)


fig = plt.figure(figsize=(50, 15))
ax1 = fig.add_subplot(111, label ="1")
ax1.grid(visible=True, which='major', color='grey', linewidth=1.0, alpha=0.2)

ax1.plot(merged_df[point_loc_field], merged_df[ahn4_field], color='grey', label="AHN4-DTM 0.50m", linewidth=3)
for index, row in merged_df.iterrows():
    if pd.notna(row[dp_loc_field]):
        ax1.annotate(row[dijkpaal_field], (row[dp_loc_field], 2), fontsize=20)
    
# ax1.plot(merged_df[dp_loc_field], 2, color='grey', label="Dijkpalen", marker = 'o')
# ax1.axhline(hoogte, color='blue', linestyle='-',linewidth=5,label=f"Leggerhoogte ({round(hoogte,1)} m NAP)")

ax1.set_title(f'Lengteprofiel {"test"}', fontsize=30, x=0.5, y=0.95)

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

plt.ylim(0, 10)

plt.savefig(plotdir + f"profile_{'test'}.png")
fig.clf()
plt.close(fig)
gc.collect()








