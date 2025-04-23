/* eslint-disable prefer-const */
/* eslint-disable @typescript-eslint/no-floating-promises */
/* eslint-disable @typescript-eslint/no-unsafe-argument */
/* eslint-disable @typescript-eslint/no-unused-vars */
/* eslint-disable @typescript-eslint/consistent-type-imports */
/* eslint-disable import/order */

import * as reactiveUtils from "@arcgis/core/core/reactiveUtils";
import {
    ComponentModelBase,
    ComponentModelProperties,
    PropertyDefs,
    serializable,
    // importModel,
} from "@vertigis/web/models";

import * as XLSX from "xlsx";

import { Features } from "@vertigis/web/messaging";
import GraphicsLayer from "esri/layers/GraphicsLayer";
import GeoJSONLayer from "esri/layers/GeoJSONLayer";
import ElevationLayer from "esri/layers/ElevationLayer";
import FeatureLayer from "esri/layers/FeatureLayer";

import Graphic from "esri/Graphic";

import Polyline from "esri/geometry/Polyline";
import Polygon from "esri/geometry/Polygon";
import Point from "esri/geometry/Point";
import Multipoint from "esri/geometry/Multipoint";
import Mesh from "esri/geometry/Mesh";

import SpatialReference from "esri/geometry/SpatialReference";
import * as geometryEngine from "esri/geometry/geometryEngine";
import * as webMercatorUtils from "esri/geometry/support/webMercatorUtils";
import * as projection from "esri/geometry/projection";
import * as meshUtils from "esri/geometry/support/meshUtils";

import SketchViewModel from "esri/widgets/Sketch";

import * as GeoJSONInterfaces from "./GeoJSONInterfaces";

export interface DikeDesignerModelProperties extends ComponentModelProperties {
    elevationLayerUrl?: string;
}
@serializable
export default class DikeDesignerModel extends ComponentModelBase<DikeDesignerModelProperties> {
    elevationLayerUrl: DikeDesignerModelProperties["elevationLayerUrl"];

    graphicsLayerLine: GraphicsLayer;
    graphicsLayerTemp: GraphicsLayer;
    graphicsLayerMesh: GraphicsLayer;
    elevationLayer: ElevationLayer;


    map: any;
    view: any;
    sketchViewModel: SketchViewModel | undefined;
    drawnLine: any;
    offsetGeometries: any[] = [];
    meshes: Mesh[] = [];
    mergedMesh: Mesh | null = null;
    meshGraphic: Graphic | null = null;
    gridSize: number = 1
    totalVolumeDifference: number = 0
    excavationVolume: number = 0
    fillVolume: number = 0

    chartData: any[] = null
    excelData: any[] = null

    chartRoot: any = null
    chart: any = null
    chartSeries: any = null

    // New method to handle GeoJSON upload
    handleGeoJSONUpload(file: File): void {
        const reader = new FileReader();

        function extractEPSG(crs: any): number | null {
            if (!crs) {
                console.warn("No CRS information found.");
                return null;
            }

            if (typeof crs === "string") {
                // Handle cases where CRS is a string (e.g., "EPSG:4326")
                const match = crs.match(/EPSG[:]*([0-9]+)/);
                return match ? parseInt(match[1]) : null;
            }

            if (crs?.properties?.name)  {
                // Handle cases where CRS is an object with a "name" property
                const name = crs.properties.name;

                // Match EPSG codes in formats like "EPSG:4326" or "urn:ogc:def:crs:EPSG::4326"
                const match = name.match(/EPSG[:]*([0-9]+)/);
                if (match) {
                    return parseInt(match[1]);
                }

                // Handle cases like "urn:ogc:def:crs:OGC:1.3:CRS84"
                if (name.includes("CRS84")) {
                    console.warn("CRS84 detected, defaulting to EPSG:4326.");
                    return 4326; // CRS84 is equivalent to EPSG:4326
                }
            }

            console.warn("Unsupported CRS format:", crs);
            return null;
        }

        reader.onload = (e) => {
            try {
                const geojson = JSON.parse(e.target?.result as string);
                console.log("Parsed GeoJSON:", geojson);
                if (!geojson?.features) {
                    console.error("Invalid GeoJSON format.");
                    return;
                }

                const inEPSG = extractEPSG(geojson.crs?.properties?.name || "");
                console.log("Input EPSG:", inEPSG);

                projection.load().then(() => {
                    geojson.features.forEach(feature => {
                        const { geometry, properties } = feature;

                        let esriGeometry;
                        const spatialRefOut = new SpatialReference({ wkid: 3857 });
                        let spatialRefIn = new SpatialReference({ wkid: inEPSG });

                        if (!inEPSG) {
                            spatialRefIn = new SpatialReference({ wkid: 4326 });
                        }



                        if (geometry.type === "LineString") {
                            esriGeometry = new Polyline({
                                paths: [geometry.coordinates],
                                spatialReference: spatialRefIn
                            });
                        } else if (geometry.type === "MultiLineString") {
                            esriGeometry = new Polyline({
                                paths: geometry.coordinates,
                                spatialReference: spatialRefIn
                            });
                        } else {
                            console.warn("Unsupported geometry type:", geometry.type);
                            return;
                        }

                        const projected = projection.project(esriGeometry, spatialRefOut);

                                    const symbol = {
                                        type: "simple-line",
                                        color: [255, 0, 255],
                                        width: 2
                                    };

                                    const graphic = new Graphic({
                                        geometry: projected as any,
                                        attributes: properties,
                                        symbol: symbol as any
                                    });

                                    this.graphicsLayerLine.add(graphic);
                                    console.log("graphic has been added")
                                    console.log(this.graphicsLayerLine, this.map)
                    })


                })

                // this.processGeoJSON(geojson, inEPSG);
            } catch (error) {
                console.error("Error parsing GeoJSON:", error);
            }
        };

        reader.readAsText(file);
    }

    startDrawingLine(){
        this.sketchViewModel.create("polyline");

        // Listen for the create event to get the geometry
        this.sketchViewModel.on("create", async (event) => {
            if (event.state === "complete") {
                const drawnLine = event.graphic.geometry;
                // console.log("Polygon geometry:", poylgonGeometry);

                // publish event to show dialog
                this.drawnLine = drawnLine;
                console.log(this.sketchViewModel)
                this.sketchViewModel.set("state", "update");

                this.sketchViewModel.update(event.graphic) // Update the graphic with the new geometry
;
            }
        });
    }

    selectLineFromMap(){
    }

    handleExcelUpload = (event: React.ChangeEvent<HTMLInputElement>) => {
        const fileInput = event.target; // Reference to the file input
        const file = fileInput.files?.[0];
        if (file) {
            const reader = new FileReader();
            reader.onload = (e) => {
                const data = new Uint8Array(e.target?.result as ArrayBuffer);
                const workbook = XLSX.read(data, { type: "array" });
                const sheetName = workbook.SheetNames[0];
                const sheet = workbook.Sheets[sheetName];
                const jsonData = XLSX.utils.sheet_to_json(sheet, { header: 1 });

                // Set Excel data for the table
                this.excelData = jsonData;
                

                // Prepare and sort chart data
                if (jsonData.length > 1) {
                    const sortedData = jsonData
                        .slice(1) // Skip the header row
                        .map((row: any[]) => ({
                            locatie: row[0], // Location name
                            afstand: row[1], // X-axis value
                            hoogte: row[2],  // Y-axis value
                        }))
                        .sort((a, b) => a.afstand - b.afstand); // Sort by afstand (X-axis)

                    this.chartData = sortedData; // Update chartData to trigger UI update
                }
            };
            reader.readAsArrayBuffer(file);
        }

        // Reset the file input value to allow reuploading the same file
        fileInput.value = "";
    };

    protected override _getSerializableProperties(): PropertyDefs<DikeDesignerModelProperties> {
        const props = super._getSerializableProperties();
        return {
            ...props,
            elevationLayerUrl: {
                serializeModes: ["initial"],
                default: "https://elevation3d.arcgis.com/arcgis/rest/services/WorldElevation3D/Terrain3D/ImageServer",
            }
        };
    }

    protected async _onInitialize(): Promise<void> {
        await super._onInitialize();

        

        this.messages.events.map.initialized.subscribe(async (map) => {
            console.log("Map initialized:", map);
            this.map = map.maps.map;
            this.view = map.maps["view"];

            this.graphicsLayerLine = new GraphicsLayer({
                title: "Temporary Layer",
                elevationInfo: {
                    mode: "on-the-ground",
                    offset: 0
                },
                listMode: "hide",
            });
            this.graphicsLayerTemp = new GraphicsLayer({
                title: "Temporary Layer",
                elevationInfo: {
                    mode: "absolute-height",
                    offset: 0
                },
                listMode: "hide",
                visible: false,
            });
            this.graphicsLayerMesh = new GraphicsLayer({
                title: "Temporary Layer",
                elevationInfo: {
                    mode: "absolute-height",
                    offset: 0
                },
                listMode: "hide",
            });
        
            this.elevationLayer = new ElevationLayer({
                url: this.elevationLayerUrl,
            });
            this.map.add(this.graphicsLayerLine);
            this.map.add(this.graphicsLayerTemp);
            this.map.add(this.graphicsLayerMesh);
        


            

            // Initialize the SketchViewModel

            // this.sketchViewModel = new SketchViewModel({
            //     view: this.view,
            //     layer: this.graphicsLayerLine,
            // });
            await reactiveUtils
            .whenOnce(() => this.view)
            .then(() => {
                
                console.log("Graphics layer added to the map.");
                
            this.sketchViewModel = new SketchViewModel({
                view: this.view,
                layer: this.graphicsLayerLine,
            });
            });
        });
    }
}
