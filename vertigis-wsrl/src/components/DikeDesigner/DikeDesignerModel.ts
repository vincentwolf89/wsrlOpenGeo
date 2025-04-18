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

import {  Features } from "@vertigis/web/messaging";
import Graphic from "@arcgis/core/Graphic";
import SpatialReference from "@arcgis/core/geometry/SpatialReference";
import Polyline from "@arcgis/core/geometry/Polyline";
import * as projection from "@arcgis/core/geometry/projection";
import FeatureSet from "@arcgis/core/rest/support/FeatureSet"
import GraphicsLayer from "@arcgis/core/layers/GraphicsLayer";
import SketchViewModel from "@arcgis/core/widgets/Sketch/SketchViewModel";

import * as GeoJSONInterfaces from "./GeoJSONInterfaces"

export interface DikeDesignerModelProperties extends ComponentModelProperties {
    selectedTheme?: string;
    netwerkLayer?: string;
}
@serializable
export default class DikeDesignerModel extends ComponentModelBase<DikeDesignerModelProperties> {
    selectedTheme: DikeDesignerModelProperties["selectedTheme"];
    netwerkLayer: DikeDesignerModelProperties["netwerkLayer"];
    graphicsLayerLine = new GraphicsLayer({
        title: "Temporary Layer",
        elevationInfo: {
            mode: "on-the-ground",
            offset: 0
        },
        listMode: "hide",
    });

    map: any;
    view: any;
    sketchViewModel: SketchViewModel;
    drawnLine: any;

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
        this.sketchViewModel.on("create", (event) => {
            if (event.state === "complete") {
                const drawnLine = event.graphic.geometry;
                // console.log("Polygon geometry:", poylgonGeometry);

                // publish event to show dialog
                this.drawnLine = drawnLine;
;
            }
        });
    }

    selectLineFromMap(){
    }

    protected override _getSerializableProperties(): PropertyDefs<DikeDesignerModelProperties> {
        const props = super._getSerializableProperties();
        return {
            ...props,
            selectedTheme: {
                serializeModes: ["initial"],
                default: "Topo donker",
            },
            netwerkLayer: {
                serializeModes: ["initial"],
                default: "LSSS Netwerk Vieww",
            },
        };
    }

    protected async _onInitialize(): Promise<void> {
        await super._onInitialize();

        

        this.messages.events.map.initialized.subscribe(async (map) => {
            console.log("Map initialized:", map);
            this.map = map.maps.map;
            this.view = map.maps["view"];
            this.map.add(this.graphicsLayerLine);

            // Initialize the SketchViewModel

            this.sketchViewModel = new SketchViewModel({
                view: this.view,
                layer: this.graphicsLayerLine,
            });
            // await reactiveUtils
            // .whenOnce(() => this.map?.view)
            // .then(() => {
                
            //     console.log("Graphics layer added to the map.");
            // });
        });
    }
}
