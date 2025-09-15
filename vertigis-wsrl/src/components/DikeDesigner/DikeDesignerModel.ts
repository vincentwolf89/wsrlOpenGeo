/* eslint-disable prefer-const */
/* eslint-disable @typescript-eslint/no-floating-promises */
/* eslint-disable @typescript-eslint/no-unsafe-argument */
/* eslint-disable @typescript-eslint/no-unused-vars */
/* eslint-disable @typescript-eslint/consistent-type-imports */
/* eslint-disable import/order */
import * as am5 from "@amcharts/amcharts5";
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
import GraphicsLayer from "@arcgis/core/layers/GraphicsLayer";
import GeoJSONLayer from "@arcgis/core/layers/GeoJSONLayer";
import ElevationLayer from "@arcgis/core/layers/ElevationLayer";
import FeatureLayer from "@arcgis/core/layers/FeatureLayer";
import UniqueValueRenderer from "@arcgis/core/renderers/UniqueValueRenderer";

import Graphic from "@arcgis/core/Graphic";

import Polyline from "@arcgis/core/geometry/Polyline";
import Polygon from "@arcgis/core/geometry/Polygon";
import Point from "@arcgis/core/geometry/Point";
import Multipoint from "@arcgis/core/geometry/Multipoint";
import Mesh from "@arcgis/core/geometry/Mesh";

import SpatialReference from "@arcgis/core/geometry/SpatialReference";
import * as geometryEngine from "@arcgis/core/geometry/geometryEngine";
import * as webMercatorUtils from "@arcgis/core/geometry/support/webMercatorUtils";
import * as projection from "@arcgis/core/geometry/projection";
import * as meshUtils from "@arcgis/core/geometry/support/meshUtils";

import SketchViewModel from "@arcgis/core/widgets/Sketch";

import { initializeChart, getLineFeatureLayers } from "./Functions/DesignFunctions";
import { array } from "@amcharts/amcharts5";
export interface DikeDesignerModelProperties extends ComponentModelProperties {
    elevationLayerUrl?: string;
}
@serializable
export default class DikeDesignerModel extends ComponentModelBase<DikeDesignerModelProperties> {

    designPanelVisible: boolean = false;
    crossSectionPanelVisible: boolean = false;

    loading: boolean = false;

    elevationLayerUrl: DikeDesignerModelProperties["elevationLayerUrl"];

    graphicsLayerLine: GraphicsLayer;
    graphicsLayerCrossSection: GraphicsLayer;
    graphicsLayerTemp: GraphicsLayer;
    graphicsLayerMesh: GraphicsLayer;
    elevationLayer: ElevationLayer;

    designLayer2D: FeatureLayer | null = null;
    uniqueParts: string[] = [];

    map: any;
    view: any;
    mapElement: HTMLElement | null = null;
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

    chartData: any[] = []
    allChartData: Record<string, any[]> = {}
    excelSheets: Record<string, any[]> = {};
    activeSheet: string = "";

    chartRoot: any = null
    chart: any = null
    chartSeries: any = null

    crossSectionChartData: any[] = null
    crossSectionChartRoot: any = null
    crossSectionChart: any = null
    meshSeriesData: any[] = null

    userLinePoints: any[] = []
    slopeLabels: am5.Label[] = []


    lineFeatureLayers: FeatureLayer[] = []
    selectedLineLayerId: string | null
    selectedLineLayer: FeatureLayer | null
    selectedDijkvakLayerFields: string[] = []
    selectedDijkvakField: string | null = null

    lineLayerSymbol = {
        type: "simple-line",
        color: [255, 0, 255],
        width: 4
    };

    // data for analysis
    intersectingPanden: object[] = []
    intersectingBomen: object[] = []
    intersectingPercelen: object[] = []

    dwpLocations: string[] = [
        "buitenteen",
        "onderkant_buitenberm",
        "bovenkant_buitenberm",
        "buitenkruin",
        "binnenkruin",
        "bovenkant_binnenberm",
        "onderkant_binnenberm",
        "binnenteen",
    ]


    overviewVisible: boolean = false

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

            if (crs?.properties?.name) {
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


                        const graphic = new Graphic({
                            geometry: projected as any,
                            attributes: properties,
                            symbol: this.lineLayerSymbol,
                        });

                        this.graphicsLayerLine.add(graphic);
                    })


                })

                // this.processGeoJSON(geojson, inEPSG);
            } catch (error) {
                console.error("Error parsing GeoJSON:", error);
            }
        };

        reader.readAsText(file);
    }
    startDrawingLine(lineLayer: GraphicsLayer): Promise<__esri.Polyline> {

        if (lineLayer?.graphics?.length > 0) {
            // Clear existing graphics if any
            lineLayer.removeAll();
        }
        this.sketchViewModel.layer = lineLayer;
        this.sketchViewModel.create("polyline");

        return new Promise((resolve, reject) => {
            const handler = this.sketchViewModel.on("create", (event: any) => {
                if (event.state === "complete") {
                    const drawnLine = event.graphic.geometry;
                    this.drawnLine = drawnLine;
                    this.sketchViewModel.set("state", "update");
                    this.sketchViewModel.update(event.graphic);

                    handler.remove(); // Clean up the event listener
                    resolve(drawnLine);
                }
                // Optionally handle cancel/error states here
                // else if (event.state === "cancel") {
                //     handler.remove();
                //     reject(new Error("Drawing cancelled"));
                // }
            });
        });
    }

    selectLineFromMap() {
    }

    initializeEmptyChartData(): void {
    if (!this.allChartData || Object.keys(this.allChartData).length === 0) {
        // Create a default empty sheet
        const defaultSheetName = "vak 1";
        const defaultData = [
            {
                locatie: "",
                afstand: "",
                hoogte: "",
            }
        ];

        this.allChartData = {
            [defaultSheetName]: defaultData
        };
        
        this.chartData = [...defaultData];
        this.activeSheet = defaultSheetName;
        
        console.log("Initialized empty chart data with default sheet");
    }
}

    // here we need to make chartData contain all the sheets and forget about the excelsheets later
    handleExcelUpload = (event: React.ChangeEvent<HTMLInputElement>) => {
        const fileInput = event.target; // Reference to the file input
        const file = fileInput.files?.[0];
        if (file) {
            const reader = new FileReader();
            reader.onload = (e) => {
                const data = new Uint8Array(e.target?.result as ArrayBuffer);
                const workbook = XLSX.read(data, { type: "array" });

                // Extract all sheets
                const sheets: Record<string, any[]> = {};
                const allChartData: Record<string, any[]> = {};
                workbook.SheetNames.forEach((sheetName) => {
                    const sheet = workbook.Sheets[sheetName];
                    const jsonData = XLSX.utils.sheet_to_json(sheet, { header: 1 });
                    sheets[sheetName] = jsonData;

                    // Prepare chart data for each sheet
                    if (jsonData.length > 1) {
                        allChartData[sheetName] = jsonData
                            .slice(1) // Skip the header row
                            .map((row: any[]) => ({
                                locatie: row[0], // Location name
                                afstand: row[1], // X-axis value
                                hoogte: row[2], // Y-axis value
                            }))
                            .sort((a, b) => a.afstand - b.afstand); // Sort by afstand
                    }
                });
                this.allChartData = allChartData; // Store all chart data
                console.log("All chart data:", this.allChartData);


                // Set the first sheet as the default table data
                const firstSheetName = workbook.SheetNames[0];
                this.chartData = allChartData[firstSheetName];
                this.activeSheet = firstSheetName;
            };
            reader.readAsArrayBuffer(file);
        }

        // Reset the file input value to allow reuploading the same file
        fileInput.value = "";
        this.overviewVisible = true;
    };

    // New method to set the table data for a selected sheet
    setSheetData(sheetName: string): void {
        const sheetData = this.excelSheets[sheetName];
        if (sheetData) {
            // Prepare and sort chart data
            if (sheetData.length > 1) {
                const sortedData = sheetData
                    .slice(1) // Skip the header row
                    .map((row: any[]) => ({
                        locatie: row[0], // Location name
                        afstand: row[1], // X-axis value
                        hoogte: row[2], // Y-axis value
                    }))
                    .sort((a, b) => a.afstand - b.afstand); // Sort by afstand (X-axis)

                this.chartData = sortedData; // Update chartData to trigger UI update
            }
        }
    }

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
        console.log("DikeDesignerModel initialized");

        this.messages.events.map.initialized.subscribe(async (map) => {
            console.log("Map initialized:", map);
            this.mapElement = document.querySelector(".gcx-map")
            this.map = map.maps.map;
            this.view = map.maps["view"];

            this.designLayer2D = new FeatureLayer({
                title: "Ontwerpdata - 2D",
                listMode: "show",
                geometryType: "polygon",
                objectIdField: "ObjectID",
                source: [],
                fields: [
                    {
                        name: "ObjectID",
                        alias: "ObjectID",
                        type: "oid"
                    },
                    {
                        name: "name",
                        alias: "Name",
                        type: "string"
                    }
                    // Add more fields if needed
                ]
            });

            // Your unique values (deduplicated)
            const uniqueNames = [
                "buitenkruin-binnenkruin",
                "buitenkruin-bovenkant_buitenberm",
                "binnenkruin-bovenkant_binnenberm",
                "bovenkant_buitenberm-onderkant_buitenberm",
                "onderkant_buitenberm-buitenteen",
                "bovenkant_binnenberm-onderkant_binnenberm",
                "onderkant_binnenberm-binnenteen"
            ];

            // Helper to pick color based on rules
            function getSymbolForName(name: string) {
                if (name.includes("berm")) {
                    // Green for berms
                    return {
                        type: "simple-fill",
                        color: [102, 204, 102, 0.9], // green
                        outline: { color: [0, 100, 0, 1], width: 1 }
                    };
                }
                if (name.includes("kruin")) {
                    // Grey for kruin
                    return {
                        type: "simple-fill",
                        color: [180, 180, 180, 0.9], // grey
                        outline: { color: [80, 80, 80, 1], width: 1 }
                    };
                }
                // Default color
                return {
                    type: "simple-fill",
                    color: [200, 200, 255, 0.9], // light blue
                    outline: { color: [100, 100, 200, 1], width: 1 }
                };
            }

            const uniqueValueInfos = uniqueNames.map(name => ({
                value: name,
                symbol: getSymbolForName(name)
            }));



            this.designLayer2D.renderer = new UniqueValueRenderer({
                field: "name",
                uniqueValueInfos,
                defaultSymbol: {
                    type: "simple-fill",
                    color: [204, 255, 204, 0.7], // light green
                    outline: { color: [0, 128, 0, 1], width: 1 }
                } as any
            });



            this.graphicsLayerLine = new GraphicsLayer({
                title: "Temporary Layer",
                elevationInfo: {
                    mode: "on-the-ground",
                    offset: 0
                },
                listMode: "hide",
            });

            this.graphicsLayerCrossSection = new GraphicsLayer({
                title: "Dwarsprofiel - tijdelijk",
                elevationInfo: {
                    mode: "on-the-ground",
                    offset: 0
                },
                listMode: "hide",
            });

            this.graphicsLayerTemp = new GraphicsLayer({
                title: "Ontwerpdata - tijdelijk",
                elevationInfo: {
                    mode: "absolute-height",
                    offset: 0
                },
                listMode: "show",
                visible: false,
            });
            this.graphicsLayerMesh = new GraphicsLayer({
                title: "Mesh layer - tijdelijk",
                elevationInfo: {
                    mode: "absolute-height",
                    offset: 0
                },
                listMode: "show",
            });


            this.elevationLayer = new ElevationLayer({
                url: this.elevationLayerUrl,
            });
            this.map.add(this.graphicsLayerLine);
            this.map.add(this.graphicsLayerCrossSection);
            this.map.add(this.graphicsLayerTemp);
            this.map.add(this.graphicsLayerMesh);
            this.map.add(this.designLayer2D);


            this.lineFeatureLayers = await getLineFeatureLayers(this.map);
            console.log("Line feature layers:", this.lineFeatureLayers);



            await reactiveUtils
                .whenOnce(() => this.view)
                .then(() => {

                    console.log("Graphics layer added to the map.");

                    this.sketchViewModel = new SketchViewModel({
                        view: this.view,
                        // layer: this.graphicsLayerLine,
                    });
                });
        });
    }
}
