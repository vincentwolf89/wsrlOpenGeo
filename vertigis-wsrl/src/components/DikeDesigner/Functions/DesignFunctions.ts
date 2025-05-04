/* eslint-disable prefer-const */
/* eslint-disable @typescript-eslint/no-floating-promises */
/* eslint-disable @typescript-eslint/no-unsafe-argument */
/* eslint-disable @typescript-eslint/no-unused-vars */
/* eslint-disable @typescript-eslint/consistent-type-imports */
/* eslint-disable import/order */

import * as am5 from "@amcharts/amcharts5";
import * as am5xy from "@amcharts/amcharts5/xy";
import am5themes_Animated from "@amcharts/amcharts5/themes/Animated";

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



export async function createDesigns(model): Promise<void> {

    let basePath: Polyline | undefined = undefined;
    let chartData: any[] = [];
    if (model.selectedDijkvakField){
        console.log("do stuff here...")
        model.graphicsLayerLine.graphics.items.forEach(async(graphic) => {
            const attributes = graphic.attributes;
            if (attributes[model.selectedDijkvakField]) {
                const dijkvakValue = attributes[model.selectedDijkvakField];
            
                // find corresponding chartdata
                chartData = model.allChartData[dijkvakValue]
                basePath = graphic.geometry

                console.log(dijkvakValue, "Dijkvak value")
                console.log(chartData, "Chart data")
                console.log(basePath, "Base path geometry")

                await createDesign(model, graphic.geometry, model.allChartData[dijkvakValue], dijkvakValue);
            }
        })
    } else {
        basePath = model.graphicsLayerLine.graphics.items[0].geometry;
        chartData = model.chartData
        createDesign(model, basePath, chartData, "default");
    }

    
    // if (model.selectedDijkvakField){
    //     console.log(model.selectedDijkvakField, "Selected dijkvak field")
    //     model.graphicsLayerLine.graphics.items.forEach((graphic) => {
    //         const attributes = graphic.attributes;
    //         if (attributes[model.selectedDijkvakField]) {
    //             const dijkvakValue = attributes[model.selectedDijkvakField];
    //             console.log(dijkvakValue, "Dijkvak value")
    //             // model.chartData.forEach((row) => {
    //             //     if (row.dijkvak === dijkvakValue) {
    //             //         row.afstand = attributes.afstand;
    //             //         row.hoogte = attributes.hoogte;
    //             //     }
    //             // });
    //         }
    //     })
    // }

    // const basePath = model.graphicsLayerLine.graphics.items[0].geometry;
    // const basePath = model.basePath

}
export async function createDesign(model, basePath, chartData, dijkvak): Promise<void> {

    
    console.log(basePath, "Base path geometry");

    let offsetGeometries = []

    await chartData.forEach((row) => {
        const offsetDistance = row.afstand || 0;
        const offsetLine = geometryEngine.offset(basePath, offsetDistance) as Polyline;
        console.log(offsetLine, "Offset line geometry");

        if (offsetLine) {
            const elevation = row.hoogte || 0;
            const updatedPaths = offsetLine.paths.map((path) =>
                path.map((coord) => [coord[0], coord[1], elevation])
            );

            const offsetGraphic = new Graphic({
                geometry: new Polyline({
                    paths: updatedPaths,
                    spatialReference: SpatialReference.WebMercator,
                }),
                symbol: {
                    type: "simple-line", // SimpleLineSymbol type
                    style: "solid",
                    color: "grey",
                    width: 1,
                } as __esri.SimpleLineSymbolProperties,
               

            });

            model.graphicsLayerTemp.add(offsetGraphic);

            if (row.locatie) {
                offsetGeometries[row.locatie] = offsetGraphic.geometry;
            } else {
                console.log("Row name is missing in the data.", row);
            }
        }
    });

    // console.log(offsetGeometries, "Offset geometries");

    // Check and create polygons only if the required values exist
    if (offsetGeometries["buitenkruin"] && offsetGeometries["binnenkruin"]) {
        createPolygonBetween(model, "buitenkruin", "binnenkruin", offsetGeometries);
    }

    const containsBerm = chartData.some((row) =>
        row.locatie?.toLowerCase().includes("berm")
    );

    if (containsBerm) {
        if (offsetGeometries["buitenkruin"] && offsetGeometries["bovenkant_buitenberm"]) {
            createPolygonBetween(model, "buitenkruin", "bovenkant_buitenberm", offsetGeometries);
        }
        if (offsetGeometries["binnenkruin"] && offsetGeometries["bovenkant_binnenberm"]) {
            createPolygonBetween(model, "binnenkruin", "bovenkant_binnenberm", offsetGeometries);
        }
        if (offsetGeometries["bovenkant_buitenberm"] && offsetGeometries["onderkant_buitenberm"]) {
            createPolygonBetween(model, "bovenkant_buitenberm", "onderkant_buitenberm", offsetGeometries);
        }
        if (offsetGeometries["onderkant_buitenberm"] && offsetGeometries["buitenteen"]) {
            createPolygonBetween(model, "onderkant_buitenberm", "buitenteen", offsetGeometries);
        }
        if (offsetGeometries["bovenkant_binnenberm"] && offsetGeometries["onderkant_binnenberm"]) {
            createPolygonBetween(model, "bovenkant_binnenberm", "onderkant_binnenberm", offsetGeometries);
        }
        if (offsetGeometries["onderkant_binnenberm"] && offsetGeometries["binnenteen"]) {
            createPolygonBetween(model, "onderkant_binnenberm", "binnenteen", offsetGeometries);
        }
    } else {
        if (offsetGeometries["buitenkruin"] && offsetGeometries["binnenkruin"]) {
            createPolygonBetween(model, "buitenkruin", "binnenkruin", [128, 0, 0, 0.9]);
        }
        if (offsetGeometries["buitenkruin"] && offsetGeometries["buitenteen"]) {
            createPolygonBetween(model, "buitenkruin", "buitenteen", offsetGeometries);
        }
        if (offsetGeometries["binnenkruin"] && offsetGeometries["binnenteen"]) {
            createPolygonBetween(model, "binnenkruin", "binnenteen", offsetGeometries);
        }
    }

    const merged = meshUtils.merge(model.meshes);
    const mergedGraphic = new Graphic({
        geometry: merged,
        symbol: {
            type: "mesh-3d",
            symbolLayers: [{ type: "fill" }],
        } as __esri.Symbol3DLayerProperties,
    });
    model.graphicsLayerMesh.add(mergedGraphic);
    model.mergedMesh = merged;
    model.meshGraphic = mergedGraphic;
}

export async function calculateVolume(model): Promise<void> {

    const gridSize = model.gridSize;

    let elevationSampler = await meshUtils.createElevationSampler(
        model.mergedMesh
    );

    // elevationSampler.demResolution.max = 5; // Set the maximum resolution for the DEM
    // elevationSampler.demResolution.min = 5; // Set the minimum resolution for the DEM

    console.log("Elevation sampler created:", elevationSampler);

    const extent = model.meshGraphic.geometry.extent;

    const pointCoordsForVolume = [];
    const groundPoints = [];

    for (let x = extent.xmin; x <= extent.xmax; x += gridSize) {
        for (let y = extent.ymin; y <= extent.ymax; y += gridSize) {
            // const point = new Point({
            //     x: x as number,
            //     y: y as number,
            //     spatialReference: SpatialReference.WebMercator
            // });




            // Query the elevation at the point, maybe batch this?
            const elevation = elevationSampler.elevationAt(x, y);
            if (elevation) {

                // Add the point to the volume calculation
                pointCoordsForVolume.push([x, y, elevation]);

                // Add the point to the ground elevation query
                groundPoints.push([x, y]);

            }
        }
    }



    console.log("All points processed:", pointCoordsForVolume);
    if (pointCoordsForVolume.length === 0) {
        console.warn("No points were processed. Ensure the mesh geometries and grid size are correct.");
        return;
    }

    // Query ground elevations for all points
    const multipointForGround = new Multipoint({
        points: groundPoints,
        spatialReference: SpatialReference.WebMercator
    });




    // this can be used to visualize the points on the map, as validation
    // const graphics = multipointForGround.points.map((point) => {
    //     const graphic = new Graphic({
    //       geometry: new Point({
    //         x: point[0], 
    //         y: point[1],
    //         spatialReference: SpatialReference.WebMercator
    //       }),
    //       symbol: {
    //         type: "simple-marker",  // Or your custom symbol for the icon
    //         color: "blue",
    //         size: "10px"
    //       } as __esri.SimpleMarkerSymbolProperties,
    //     });
    //     return graphic;
    //   });
    // model.graphicsLayerLine.addMany(graphics);


    const groundResult = await model.elevationLayer.queryElevation(multipointForGround, { returnSampleInfo: true });
    console.log("Ground elevation query result:", groundResult);

    let totalVolumeDifference = 0;
    let excavationVolume = 0;
    let fillVolume = 0;

    groundResult.geometry.points.forEach(([x, y, zGround], index) => {
        const z3D = pointCoordsForVolume[index][2]; // Z value from the mesh geometry
        const volumeDifference = (z3D - zGround) * model.gridSize * model.gridSize; // Volume difference for this point

        if (volumeDifference > 0) {
            fillVolume += volumeDifference; // Fill volume (material to be added)
        } else {
            excavationVolume += Math.abs(volumeDifference); // Cut volume (material to be removed)
        }

        totalVolumeDifference += volumeDifference;
    });

    model.excavationVolume = excavationVolume.toFixed(2);
    model.fillVolume = fillVolume.toFixed(2);
    model.totalVolumeDifference = totalVolumeDifference.toFixed(2);

    console.log("Total volume difference:", totalVolumeDifference, "m³");
    console.log("Total cut volume:", excavationVolume, "m³");
    console.log("Total fill volume:", fillVolume, "m³");


}



function createMeshFromPolygon(model, polygon, textureUrl = null) {

    const mesh = Mesh.createFromPolygon(polygon, {

    });
    mesh.spatialReference = polygon.spatialReference

    const symbol = {
        type: "mesh-3d",
        symbolLayers: [{ type: "fill" }]
    };

    model.meshes.push(mesh);

    // graphicsLayerTemp.add(new Graphic({ geometry: mesh, symbol, attributes: { footprint: polygon } }));
}
function createPolygonBetween(model, nameA, nameB, offsetGeometries) {
    console.log(nameA, nameB, offsetGeometries, "createPolygonBetween function called");
    const geomA = offsetGeometries[nameA];
    const geomB = offsetGeometries[nameB];
    if (!geomA || !geomB) {
        console.warn(`Could not find lines for ${nameA} and/or ${nameB}`);
        return;
    }

    const pathA = geomA.paths[0];
    const pathB = geomB.paths[0].slice().reverse();
    let ring = pathA.concat(pathB);
    ring.push(pathA[0]);

    const polygon = new Polygon({
        rings: [ring],
        spatialReference: geomA.spatialReference
    });

    const graphic = new Graphic({
        geometry: polygon,
        attributes: { name: `${nameA}-${nameB}` }
    });

    model.graphicsLayerTemp.add(graphic);

    // featureLayerDesign.applyEdits({
    //     addFeatures: [graphic]
    // });

    createMeshFromPolygon(model, polygon, null);
}

export function exportGraphicsLayerAsGeoJSON(model): void {
    const geojson = {
        type: "FeatureCollection",
        crs: {
            type: "name",
            properties: { name: "EPSG:4326" }, // Set CRS to WGS84
        },
        features: [],
    };

    // Ensure the projection module is loaded
    projection.load().then(() => {
        model.graphicsLayerTemp.graphics.forEach((graphic) => {
            const geometry = graphic.geometry;

            if (geometry) {
                // Project the geometry to WGS84 (EPSG:4326)
                const projectedGeometry = projection.project(
                    geometry,
                    new SpatialReference({ wkid: 4326 })
                );

                if (projectedGeometry) {
                    let feature: any = {
                        type: "Feature",
                        geometry: null,
                        properties: graphic.attributes || {}, // Include graphic attributes as properties
                    };

                    // Handle different geometry types
                    if (!Array.isArray(projectedGeometry) && projectedGeometry.type === "polygon") {
                        feature.geometry = {
                            type: "Polygon",
                            coordinates: (projectedGeometry as __esri.Polygon).rings,
                        };
                        geojson.features.push(feature);
                    }

                    // geojson.features.push(feature);
                }
            }
        });

        // Create and download the GeoJSON file
        const blob = new Blob([JSON.stringify(geojson, null, 2)], { type: "application/json" });
        const url = URL.createObjectURL(blob);

        const a = document.createElement("a");
        a.href = url;
        a.download = "ontwerp_export.geojson";
        document.body.appendChild(a);
        a.click();
        document.body.removeChild(a);
    });
}

export function initializeChart(model, activeTab, chartContainerRef): () => void {
    if (activeTab !== 0 || !model.chartData || !chartContainerRef.current) {
        console.log(activeTab, model.chartData, chartContainerRef.current, "Chart not initialized");
        return
    }


    model.chartRoot = am5.Root.new(chartContainerRef.current);
    const root = model.chartRoot as am5.Root;
    root.setThemes([am5themes_Animated.new(root)]);

    const chart = root.container.children.push(
        am5xy.XYChart.new(root, {
            panX: true,
            panY: true,
            wheelX: "panX",
            wheelY: "zoomX",
            pinchZoomX: true,
        })
    );

    try {
        root._logo.dispose();
    } catch {
        // Handle error if logo is not present
    }

    const xAxis = chart.xAxes.push(
        am5xy.ValueAxis.new(root, {
            renderer: am5xy.AxisRendererX.new(root, {}),
            tooltip: am5.Tooltip.new(root, {}),
        })
    );

    const yAxis = chart.yAxes.push(
        am5xy.ValueAxis.new(root, {
            renderer: am5xy.AxisRendererY.new(root, {}),
            tooltip: am5.Tooltip.new(root, {}),
        })
    );

    const series = chart.series.push(
        am5xy.LineSeries.new(root, {
            name: "Hoogte vs Afstand",
            xAxis: xAxis as any,
            yAxis: yAxis as any,
            valueYField: "hoogte",
            valueXField: "afstand",
            tooltip: am5.Tooltip.new(root, {
                labelText: "{valueY}",
            }),
        })
    );

    series.data.setAll(model.chartData);

    series.strokes.template.setAll({
        strokeWidth: 2,
    });

    // Add draggable bullets with snapping logic
    series.bullets.push((root, series, dataItem) => {
        const circle = am5.Circle.new(root, {
            radius: 5,
            fill: root.interfaceColors.get("background"),
            stroke: series.get("fill"),
            strokeWidth: 2,
            draggable: true,
            interactive: true,
            cursorOverStyle: "pointer",
        });

        // Snap the coordinates to the nearest 0.5 meter
        const snapToGrid = (value: number, gridSize: number) => Math.round(value / gridSize) * gridSize;

        circle.events.on("dragstop", () => {
            // Calculate new positions
            const newY = yAxis.positionToValue(
                yAxis.coordinateToPosition(circle.y())
            );
            const newX = xAxis.positionToValue(
                xAxis.coordinateToPosition(circle.x())
            );

            // Snap to nearest 0.5 meter grid
            const snappedX = snapToGrid(newX, 0.5);
            const snappedY = snapToGrid(newY, 0.5);

            // Update chart
            dataItem.set("valueY", snappedY);
            dataItem.set("valueX", snappedX);

            // Update model.chartData
            const index = model.chartData.findIndex(
                (d) => d.afstand === dataItem.dataContext["afstand"]
            );

            console.log(index)

            if (index !== -1) {
                model.chartData[index].hoogte = snappedY;
                model.chartData[index].afstand = snappedX;
                
                
                model.chartData = [...model.chartData]; // Force reactivity
                model.allChartData[model.activeSheet] = [...model.chartData]; 
            }
        });

        return am5.Bullet.new(root, {
            sprite: circle,
        });
    });

    chart.set("cursor", am5xy.XYCursor.new(root, {}));

    return () => {
        root.dispose();
    };
}

export async function getLineFeatureLayers(map): Promise<FeatureLayer[]> {
    if (!map) {
        console.error("Map is not initialized.");
        return [];
    }

    // Filter layers with line geometry
    const lineFeatureLayers = map.layers
        .filter((layer) => layer.type === "feature")
        .filter((layer: FeatureLayer) => layer.geometryType === "polyline");

    console.log("Line Feature Layers:", lineFeatureLayers);
    return lineFeatureLayers as FeatureLayer[];
}

export function setInputLineFromFeatureLayer(model) {
    const inputLineFeatureLayer = model.map.layers.find((layer) => layer.id === model.selectedLineLayerId) as FeatureLayer;
    //  find featurelayer with line geometry
    const lineGeometry = inputLineFeatureLayer.queryFeatures({
        where: "1=1",
        returnGeometry: true,
        outFields: ["*"],
    }).then(async (result) => {
        const features = result.features;
        if (features.length > 0) {
            features.forEach((feature) => {

                const lineGeometry = feature.geometry;
                projection.load().then(() => {
                    const projectedGeometry = projection.project(
                        lineGeometry,
                        new SpatialReference({ wkid: 3857 })
                    );
                    model.graphicsLayerLine.add(new Graphic({
                        geometry: projectedGeometry as __esri.Geometry,
                        symbol: model.lineLayerSymbol,
                        attributes: feature.attributes,
                    }));
                    console.log(model.graphicsLayerLine, "graphicsLayerLine")

                })
            })

        } else {
            console.warn("No features found in the selected feature layer.");
        }
    }).catch((error) => {
        console.error("Error querying feature layer:", error);
    })

}