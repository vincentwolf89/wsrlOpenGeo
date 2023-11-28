import arcpy
arcpy.env.overwriteOutput = True
arcpy.env.workspace = r"C:\Users\vince\Mijn Drive\WSRL\safe_data\safe_data\safe_data.gdb"

temp_tin = r"C:\Users\vince\Mijn Drive\WSRL\safe_data\safe_data\tin"
in_features = "safe_3D_KA2_ruimtebeslag"
cash_location = r"C:\Users\vince\Mijn Drive\WSRL\safe_data\safe_data\cash"


# arcpy.CreateTin_3d(
#     out_tin=temp_tin,
#     spatial_reference='PROJCS["RD_New",GEOGCS["GCS_Amersfoort",DATUM["D_Amersfoort",SPHEROID["Bessel_1841",6377397.155,299.1528128]],PRIMEM["Greenwich",0.0],UNIT["Degree",0.0174532925199433]],PROJECTION["Double_Stereographic"],PARAMETER["False_Easting",155000.0],PARAMETER["False_Northing",463000.0],PARAMETER["Central_Meridian",5.38763888888889],PARAMETER["Scale_Factor",0.9999079],PARAMETER["Latitude_Of_Origin",52.15616055555555],UNIT["Meter",1.0]]',
#     in_features="{} SHAPE.Z Mass_Points OBJECTID".format(in_features),
#     constrained_delaunay="DELAUNAY"
# )


arcpy.management.RepairGeometry(
    in_features=in_features,
    delete_null="DELETE_NULL",
    validation_method="ESRI"
)


arcpy.management.FeatureVerticesToPoints(
    in_features=in_features,
    out_feature_class="temp_points_fortin",
    point_location="ALL"
)

arcpy.CreateTin_3d(
    out_tin=temp_tin,
    spatial_reference='PROJCS["RD_New",GEOGCS["GCS_Amersfoort",DATUM["D_Amersfoort",SPHEROID["Bessel_1841",6377397.155,299.1528128]],PRIMEM["Greenwich",0.0],UNIT["Degree",0.0174532925199433]],PROJECTION["Double_Stereographic"],PARAMETER["False_Easting",155000.0],PARAMETER["False_Northing",463000.0],PARAMETER["Central_Meridian",5.38763888888889],PARAMETER["Scale_Factor",0.9999079],PARAMETER["Latitude_Of_Origin",52.15616055555555],UNIT["Meter",1.0]]',
    in_features="temp_points_fortin SHAPE.Z Mass_Points OBJECTID",
    constrained_delaunay="DELAUNAY"
)



arcpy.ddd.TinRaster(
    in_tin=temp_tin,
    out_raster="temp_tin_raster",
    data_type="FLOAT",
    method="LINEAR",
    sample_distance="CELLSIZE",
    z_factor=1,
    sample_value=0.5
)

arcpy.management.Clip(
    in_raster="temp_tin_raster",
    rectangle="#",
    out_raster="temp_tin_raster_clip",
    in_template_dataset=in_features,
    nodata_value="3,4e+38",
    clipping_geometry="ClippingGeometry",
    maintain_clipping_extent="MAINTAIN_EXTENT"
)

arcpy.management.ProjectRaster(
    in_raster="temp_tin_raster_clip",
    out_raster="temp_tin_raster_clip_projected",
    out_coor_system='PROJCS["WGS_1984_Web_Mercator_Auxiliary_Sphere",GEOGCS["GCS_WGS_1984",DATUM["D_WGS_1984",SPHEROID["WGS_1984",6378137.0,298.257223563]],PRIMEM["Greenwich",0.0],UNIT["Degree",0.0174532925199433]],PROJECTION["Mercator_Auxiliary_Sphere"],PARAMETER["False_Easting",0.0],PARAMETER["False_Northing",0.0],PARAMETER["Central_Meridian",0.0],PARAMETER["Standard_Parallel_1",0.0],PARAMETER["Auxiliary_Sphere_Type",0.0],UNIT["Meter",1.0]]',
    resampling_type="NEAREST",
    cell_size="0,499994345784074 0,499976055397925",
    geographic_transform="Amersfoort_To_WGS_1984_NTv2",
    Registration_Point=None,
    in_coor_system='PROJCS["RD_New",GEOGCS["GCS_Amersfoort",DATUM["D_Amersfoort",SPHEROID["Bessel_1841",6377397.155,299.1528128]],PRIMEM["Greenwich",0.0],UNIT["Degree",0.0174532925199433]],PROJECTION["Double_Stereographic"],PARAMETER["False_Easting",155000.0],PARAMETER["False_Northing",463000.0],PARAMETER["Central_Meridian",5.38763888888889],PARAMETER["Scale_Factor",0.9999079],PARAMETER["Latitude_Of_Origin",52.15616055555555],UNIT["Meter",1.0]]',
    vertical="NO_VERTICAL"
)



arcpy.management.ManageTileCache(
    in_cache_location= cash_location,
    manage_mode="RECREATE_ALL_TILES",
    in_cache_name="cash_{}".format(in_features),
    in_datasource="temp_tin_raster_clip_projected",
    tiling_scheme="ARCGISONLINE_ELEVATION_SCHEME",
    import_tiling_scheme=None,
    scales=[577790.554289,288895.277144,144447.638572,72223.819286,36111.909643,18055.954822,9027.977411,4513.988705,2256.994353],
    # area_of_interest=r"in_memory\feature_set1",
    max_cell_size=None,
    min_cached_scale=577790.554289,
    max_cached_scale=2256.994353
)

arcpy.management.ExportTileCache(
    in_cache_source=cash_location+"\cash_{}".format(in_features),
    in_target_cache_folder=cash_location,
    in_target_cache_name="cash_pack_{}".format(in_features),
    export_cache_type="TILE_PACKAGE_TPKX",
    storage_format_type="COMPACT",
    scales=[1155581.108577,577790.554289,288895.277144,144447.638572,72223.819286,36111.909643,18055.954822,9027.977411,4513.988705],
    # area_of_interest=r"in_memory\feature_set1"
)


