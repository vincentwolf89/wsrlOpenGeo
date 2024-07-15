import arcpy
arcpy.env.overwriteOutput = True
from arcpy.sa import *

arcpy.env.workspace = r"C:\Users\vince\Documents\ArcGIS\Projects\safe_lengteprofielen_072024\safe_lengteprofielen_072024.gdb"

# inputs
input_trajects = "testvak"
input_dijkpalen = "dijkpalen_safe_rd"
ahn4_raster = "https://tiles.arcgis.com/tiles/nSZVuSZjHpEZZbRo/arcgis/rest/services/Elevation_3D_RD/ImageServer"
raster_1 = r"C:\Users\vince\Documents\ArcGIS\Projects\safe ahn\safe ahn.gdb\safe_ahn4_200mbuffer"
dijkvak_field = "Vaknaam"
dijkpaal_field = "rftident"
# fields
ahn4_field = "ahn4"
raster_1_field = "raster1"

point_distance = 1 # m 

# werkdata
point_layer = "temp_pointlayer"


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
    out_feature_class="temp_dijkpalen_trajects",
    join_operation="JOIN_ONE_TO_ONE",
    join_type="KEEP_ALL",
    match_option="CLOSEST",
    search_radius=None,
    distance_field_name="",
    match_fields=None
)

arcpy.lr.LocateFeaturesAlongRoutes(
    in_features="temp_dijkpalen_trajects",
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
    in_data="temp_dijkpalen_trajects",
    in_field=dijkpaal_field,
    join_table="temp_dijkpalen_table",
    join_field=dijkpaal_field,
    fields="dp_loc",
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

print ("done")








