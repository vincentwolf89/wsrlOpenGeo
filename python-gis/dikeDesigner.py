import arcpy
from itertools import groupby
from base import CopyParallelR, CopyParallelL

arcpy.env.workspace  = r"C:\Users\vince\Documents\ArcGIS\Projects\3d ontwerpen safe 2023\3d ontwerpen safe 2023.gdb"
arcpy.env.overwriteOutput = True


# temp variables
tempTin = r"C:\Users\vince\Documents\ArcGIS\Projects\3d ontwerpen safe 2023\temp\temp_tin"
designFeatures ="testFeatures"
designPartFeatures = "testParts"
dikeSegmentsForIter = "dikeSections"


trajectory = "trajectlijn_safe_rd"
dikeSegments = "test_dijkvakken"
bikLine = "safe_binnenkruinlijn_rd"

inputXls = r"C:\Users\vince\Documents\ArcGIS\Projects\3d ontwerpen safe 2023\input\demoset_1.xlsx"
inputSheet = "Blad5"
inputTable = "designTable"
groupbyField = "dijkvak"
designFields = ["dijkvak","onderdeel","start_offset","end_offset","start_z","end_z","referentie"]
ahnRaster = r"C:\Users\vince\Documents\ArcGIS\Projects\safe ahn\safe ahn.gdb\safe_ahn4_ahn2_200mbuffer"



# lists
designMergeList = []

# read designs
arcpy.conversion.ExcelToTable(
    Input_Excel_File=inputXls,
    Output_Table= inputTable,
    Sheet=inputSheet,
    field_names_row=1,
    cell_range=""
)



# create new featureClasses
arcpy.management.CreateFeatureclass(arcpy.env.workspace, designFeatures, "POLYLINE", spatial_reference = arcpy.Describe(trajectory).spatialReference)
arcpy.management.CreateFeatureclass(arcpy.env.workspace, designPartFeatures, "POLYLINE", spatial_reference = arcpy.Describe(trajectory).spatialReference)
arcpy.management.CreateFeatureclass(arcpy.env.workspace, dikeSegmentsForIter, "POLYLINE", spatial_reference = arcpy.Describe(trajectory).spatialReference)

# add fields
arcpy.management.AddField(designFeatures, "dijkvak", "TEXT", field_length=200)
arcpy.management.AddField(designFeatures, "onderdeel", "TEXT", field_length=200)

arcpy.AddField_management(designFeatures, "offset", "DOUBLE", 2, field_is_nullable="NULLABLE")
arcpy.AddField_management(designFeatures, "z", "DOUBLE", 2, field_is_nullable="NULLABLE")

arcpy.management.AddField(designPartFeatures, "dijkvak", "TEXT", field_length=200)
arcpy.management.AddField(designPartFeatures, "onderdeel", "TEXT", field_length=200)

arcpy.management.AddField(dikeSegmentsForIter, "dijkvak", "TEXT", field_length=200)


def creator():
# iterate over design, groupby 
    with arcpy.da.SearchCursor(inputTable, designFields) as cursor:
        for dijkvak, g in groupby(cursor, lambda x: x[0]):

            print (dijkvak, "loop1")
            tempLayer = arcpy.MakeFeatureLayer_management(dikeSegments,"templayer")
            arcpy.management.SelectLayerByAttribute(tempLayer, "NEW_SELECTION", "dijkvak = '{}'".format(dijkvak))
            dikeSegmentSelect = arcpy.management.CopyFeatures(tempLayer, "tempSelect")

                
            # dsCur = arcpy.da.InsertCursor(dikeSegmentsForIter, ["SHAPE@","dijkvak"])
            # # get ref
            # for row in g:
            #     ref = row[6]
            #     break
            # print (ref)

            # if ref =="bik":
            #     # transects on endpoints
            #     arcpy.management.GenerateTransectsAlongLines(
            #         in_features=dikeSegmentSelect,
            #         out_feature_class="tempTransects",
            #         interval="99999 Meters",
            #         transect_length="60 Meters",
            #         include_ends="END_POINTS"
            #     )

            #     arcpy.analysis.Intersect(
            #         in_features="tempTransects #;{} #".format(bikLine),
            #         out_feature_class="tempSplitpoints",
            #         join_attributes="ALL",
            #         output_type="POINT"
            #     )

            #     arcpy.management.SplitLineAtPoint(
            #         in_features=bikLine,
            #         point_features="tempSplitpoints",
            #         out_feature_class="tempBikParts",
            #         search_radius="0.1 Meters"
            #     )
            #     # create profile on midpoint dike section
            #     sectionLength = round(([f[0] for f in arcpy.da.SearchCursor(dikeSegmentSelect, 'SHAPE@LENGTH')][0]),0)
            #     print (sectionLength)
            #     arcpy.management.GenerateTransectsAlongLines(
            #         in_features=dikeSegmentSelect,
            #         out_feature_class="tempTransectMid",
            #         interval="{} Meters".format(sectionLength/2),
            #         transect_length="60 Meters",
            #         include_ends="NO_END_POINTS"
            #     )

            #     # select intersecting part of bikpart with mid section
            #     tempLayer = arcpy.MakeFeatureLayer_management("tempBikParts","templayer")
            #     arcpy.management.SelectLayerByLocation(
            #         in_layer=tempLayer,
            #         overlap_type="INTERSECT",
            #         select_features="tempTransectMid",
            #         search_distance=None,
            #         selection_type="NEW_SELECTION",
            #         invert_spatial_relationship="NOT_INVERT"
            #     )
            #     bikSegmentSelect = arcpy.management.CopyFeatures("templayer", "tempBikSelect")
            #     bikSegmentGeom = ([g[0] for g in arcpy.da.SearchCursor("tempBikSelect", 'SHAPE@')][0])
            #     dsCur.insertRow((bikSegmentGeom, dijkvak))

            #     dikeSegmentSelect = bikSegmentSelect

            # else:

            #     segmentGeom = ([g[0] for g in arcpy.da.SearchCursor(dikeSegmentSelect, 'SHAPE@')][0])
            #     dsCur.insertRow((segmentGeom, dijkvak))

            # del dsCur

            rowCount = 0


            for row in g:
                dijkvak = row[0]
                onderdeel = row[1]
                start_offset = row[2]
                end_offset = row[3]
                start_z = row[4]
                end_z = row[5]
                ref = row[6]

                # test
                if rowCount == 0:
                    dsCur = arcpy.da.InsertCursor(dikeSegmentsForIter, ["SHAPE@","dijkvak"])

                    print (ref,"test")

                    if ref =="bik":
                        # transects on endpoints
                        arcpy.management.GenerateTransectsAlongLines(
                            in_features=dikeSegmentSelect,
                            out_feature_class="tempTransects",
                            interval="99999 Meters",
                            transect_length="60 Meters",
                            include_ends="END_POINTS"
                        )

                        arcpy.analysis.Intersect(
                            in_features="tempTransects #;{} #".format(bikLine),
                            out_feature_class="tempSplitpoints",
                            join_attributes="ALL",
                            output_type="POINT"
                        )

                        arcpy.management.SplitLineAtPoint(
                            in_features=bikLine,
                            point_features="tempSplitpoints",
                            out_feature_class="tempBikParts",
                            search_radius="0.1 Meters"
                        )
                        # create profile on midpoint dike section
                        sectionLength = round(([f[0] for f in arcpy.da.SearchCursor(dikeSegmentSelect, 'SHAPE@LENGTH')][0]),0)
                        print (sectionLength)
                        arcpy.management.GenerateTransectsAlongLines(
                            in_features=dikeSegmentSelect,
                            out_feature_class="tempTransectMid",
                            interval="{} Meters".format(sectionLength/2),
                            transect_length="60 Meters",
                            include_ends="NO_END_POINTS"
                        )

                        # select intersecting part of bikpart with mid section
                        tempLayer = arcpy.MakeFeatureLayer_management("tempBikParts","templayer")
                        arcpy.management.SelectLayerByLocation(
                            in_layer=tempLayer,
                            overlap_type="INTERSECT",
                            select_features="tempTransectMid",
                            search_distance=None,
                            selection_type="NEW_SELECTION",
                            invert_spatial_relationship="NOT_INVERT"
                        )
                        bikSegmentSelect = arcpy.management.CopyFeatures("templayer", "tempBikSelect")
                        bikSegmentGeom = ([g[0] for g in arcpy.da.SearchCursor("tempBikSelect", 'SHAPE@')][0])
                        dsCur.insertRow((bikSegmentGeom, dijkvak))

                        dikeSegmentSelect = bikSegmentSelect

                    else:

                        segmentGeom = ([g[0] for g in arcpy.da.SearchCursor(dikeSegmentSelect, 'SHAPE@')][0])
                        dsCur.insertRow((segmentGeom, dijkvak))

                    del dsCur

                # test end



                rowCount += 1
                print (onderdeel,"onderdeel")

                # copy parallel
                with arcpy.da.SearchCursor(dikeSegmentSelect, ("Shape@")) as sCur:
                    for line in sCur:

                        dfCur = arcpy.da.InsertCursor(designFeatures, ["SHAPE@","dijkvak","onderdeel","offset","z"])


                        if start_offset <= 0: # river section
                            offsetLineStart = CopyParallelR(line[0], abs(start_offset))
                            dfCur.insertRow((offsetLineStart, dijkvak,onderdeel,start_offset,start_z))

                        if start_offset > 0: # dike section
                            offsetLineStart = CopyParallelL(line[0], start_offset)
                            dfCur.insertRow((offsetLineStart, dijkvak,onderdeel,start_offset,start_z))
        
                        if end_offset <= 0:
                            offsetLineEnd = CopyParallelR(line[0], abs(end_offset))
                            dfCur.insertRow((offsetLineEnd, dijkvak,onderdeel,end_offset,end_z))
                        if end_offset > 0:
                            offsetLineEnd = CopyParallelL(line[0], end_offset)
                            dfCur.insertRow((offsetLineEnd, dijkvak,onderdeel,end_offset,end_z))

                        del dfCur

                        dpCur = arcpy.da.InsertCursor(designPartFeatures, ["SHAPE@","dijkvak","onderdeel"])

                        
                            
                        # middle part for joining onderdeel
                        
                        if end_offset <= 0:
                            middleOffset = abs(start_offset)+(abs(end_offset-start_offset)/2)
                            offsetLineMiddle = CopyParallelR(line[0], middleOffset)
                            dpCur.insertRow((offsetLineMiddle, dijkvak,onderdeel))
                        if end_offset > 0:
                            middleOffset = start_offset+(abs(end_offset-start_offset)/2)
                            offsetLineMiddle = CopyParallelL(line[0], middleOffset)
                            dpCur.insertRow((offsetLineMiddle, dijkvak,onderdeel))

                        del dpCur
                        


    # #iterate over created features per section
    with arcpy.da.SearchCursor(designFeatures, ["dijkvak","onderdeel","offset","z"]) as cursor:
        for sectionName, g in groupby(cursor, lambda x: x[0]):
            print (sectionName ,"loop2")

            sectionNameForOutput = sectionName.replace("+","_")
            

            # save items in separate featureclass
            tempLayer = arcpy.MakeFeatureLayer_management(designFeatures,"templayer")
            tempSelect = arcpy.management.SelectLayerByAttribute(tempLayer, "NEW_SELECTION", "dijkvak = '{}'".format(sectionName))
            designFeaturesSelect= arcpy.management.CopyFeatures(tempLayer, "tempDesignfeatures")

            # get dike segment
            tempLayer = arcpy.MakeFeatureLayer_management(dikeSegmentsForIter,"templayer")
            tempSelect = arcpy.management.SelectLayerByAttribute(tempLayer, "NEW_SELECTION", "dijkvak = '{}'".format(sectionName))
            dikeSegmentSelect= arcpy.management.CopyFeatures(tempLayer, "tempSelectDikesection")

                
            arcpy.management.GenerateTransectsAlongLines(
                in_features=dikeSegmentSelect,
                out_feature_class="tempTransects",
                interval="99999 Meters",
                transect_length="300 Meters",
                include_ends="END_POINTS"
            )

            # create endpoints on designfeature
            arcpy.management.FeatureVerticesToPoints(
                in_features=designFeaturesSelect,
                out_feature_class="tempEndpointsDesignfeatures",
                point_location="BOTH_ENDS"
            )


            # create endpoints on dike segments
            arcpy.management.FeatureVerticesToPoints(
                in_features=dikeSegmentSelect,
                out_feature_class="tempEndpointsDikesegment",
                point_location="BOTH_ENDS"
            )

            # create minimum bounding geometry
            arcpy.management.MinimumBoundingGeometry(
                in_features=designFeaturesSelect,
                out_feature_class="tempBoundary",
                geometry_type="CONVEX_HULL",
                group_option="ALL",
                group_field=None,
                mbg_fields_option="NO_MBG_FIELDS"
            )

            # split transects with endpoints designfeatures
            arcpy.management.SplitLineAtPoint(
                in_features="tempTransects",
                point_features="tempEndpointsDesignfeatures",
                out_feature_class="tempTransectParts",
                search_radius="0.1 Meters"
            )

            # select parts of transects within bouding geometry
        
            tempLayer = arcpy.MakeFeatureLayer_management("tempTransectParts","templayer")
            arcpy.management.SelectLayerByLocation(
                in_layer=tempLayer,
                overlap_type="WITHIN",
                select_features="tempBoundary",
                search_distance=None,
                selection_type="NEW_SELECTION",
                invert_spatial_relationship="NOT_INVERT"
            )
            selectedTransectparts = arcpy.management.CopyFeatures(tempLayer, "tempSelectedTransectparts")

            # merge 
            arcpy.management.Merge(
                inputs="{};tempSelectedTransectparts".format(designFeaturesSelect),
                output="tempMerge",
                add_source="NO_SOURCE_INFO"
            )

            # feature to 3d
            arcpy.ddd.FeatureTo3DByAttribute(
                in_features="tempMerge",
                out_feature_class="tempDesigns3dLines",
                height_field="z",
                to_height_field=None
            )


            # tin 
            arcpy.ddd.CreateTin(
                out_tin= tempTin,
                spatial_reference=arcpy.Describe(trajectory).spatialReference,
                in_features="tempMerge z Hard_Line <None>",
                constrained_delaunay="DELAUNAY"
            )

            # tin edge
            arcpy.ddd.TinEdge(
                in_tin=tempTin,
                out_feature_class="tempTinEdges",
                edge_type="ALL"
            )

            # feature to polygon
            arcpy.management.FeatureToPolygon(
                in_features="tempTinEdges",
                out_feature_class="temp3dPoly",
                cluster_tolerance=None,
                attributes="ATTRIBUTES",
                label_features=None
            )
            # tempmerge to polygon to select relevant 3d pieces
            arcpy.management.FeatureToPolygon(
                in_features="tempMerge",
                out_feature_class="temp3dBoundary",
                cluster_tolerance=None,
                attributes="ATTRIBUTES",
                label_features=None
            )

            tempLayer = arcpy.MakeFeatureLayer_management("temp3dPoly","templayer")
            arcpy.management.SelectLayerByLocation(
                in_layer=tempLayer,
                overlap_type="WITHIN",
                select_features="temp3dBoundary",
                search_distance=None,
                selection_type="NEW_SELECTION",
                invert_spatial_relationship="NOT_INVERT"
            )
            selected3dParts = arcpy.management.CopyFeatures(tempLayer, "tempSelected3dParts_{}".format(sectionNameForOutput))

            # spatial join
            arcpy.analysis.SpatialJoin(
                target_features="tempSelected3dParts_{}".format(sectionNameForOutput),
                join_features="testParts",
                out_feature_class="tempSelected3dPartsSjoin_{}".format(sectionNameForOutput),
                join_operation="JOIN_ONE_TO_ONE",
                join_type="KEEP_ALL",
                match_option="INTERSECT",
                search_radius=None,
                distance_field_name=""
            )

            # pairwise dissolve
            arcpy.analysis.PairwiseDissolve(
                in_features="tempSelected3dPartsSjoin_{}".format(sectionNameForOutput),
                out_feature_class="designs3d_{}".format(sectionNameForOutput),
                dissolve_field="onderdeel",
                statistics_fields=None,
                multi_part="MULTI_PART",
                concatenation_separator=""
            )

            # add and calculate field for design parts name
            arcpy.AddField_management("designs3d_{}".format(sectionNameForOutput), "dijkvak", "TEXT")
            arcpy.CalculateField_management("designs3d_{}".format(sectionNameForOutput), "dijkvak", sectionNameForOutput, "PYTHON")
        

            # add to merge list
            designMergeList.append("designs3d_{}".format(sectionNameForOutput))



def afterwork():
    # # merge 
    # arcpy.management.Merge(
    #     inputs=designMergeList,
    #     output="mergedDesignPolys",
    #     add_source="NO_SOURCE_INFO"
    # )

    # create tin again
    arcpy.ddd.CreateTin(
        out_tin=tempTin,
        spatial_reference=arcpy.Describe(trajectory).spatialReference,
        in_features="mergedDesignPolys Shape.Z Soft_Clip <None>",
        constrained_delaunay="DELAUNAY"
    )

    # create raster from tin
    arcpy.ddd.TinRaster(
        in_tin=tempTin,
        out_raster="tempDesignRaster",
        data_type="FLOAT",
        method="LINEAR",
        sample_distance="CELLSIZE",
        z_factor=1,
        sample_value=1
    )


    # cut fill with ahn
    arcpy.ddd.CutFill(
        in_before_surface="safe_ahn4_200mbuffer",
        in_after_surface="tempDesignRaster",
        out_raster="tempCutFillRaster",
        z_factor=1
    )

    # get only negative values from cut-fill
    arcpy.management.MakeRasterLayer(in_raster="tempCutFillRaster", out_rasterlayer="tempraster")
    arcpy.management.SelectLayerByAttribute(
        in_layer_or_view="tempraster",
        selection_type="NEW_SELECTION",
        where_clause="VOLUME < 0",
        invert_where_clause=None
    )

    arcpy.management.CopyRaster(in_raster="tempraster", out_rasterdataset="tempCutFillSelect")


    # # output to json
    # arcpy.conversion.FeaturesToJSON(
    #     in_features="mergedDesignPolys",
    #     out_json_file=r"C:\Users\vince\Documents\ArcGIS\Projects\3d ontwerpen safe 2023\json\safe_designtests_13_05_2023.geojson",
    #     format_json="NOT_FORMATTED",
    #     include_z_values="Z_VALUES",
    #     include_m_values="NO_M_VALUES",
    #     geoJSON="GEOJSON",
    #     use_field_alias="USE_FIELD_NAME"
    # )

    # # iterate over designs elements and get surface with cut-fill
    # dCur = arcpy.da.UpdateCursor("mergedDesignPolys",)

afterwork()
arcpy.management.SelectLayerByAttribute(
    in_layer_or_view="tempCutFillRaster",
    selection_type="NEW_SELECTION",
    where_clause="VOLUME < 0",
    invert_where_clause=None
)