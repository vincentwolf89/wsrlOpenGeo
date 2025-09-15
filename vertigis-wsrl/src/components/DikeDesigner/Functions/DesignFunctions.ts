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
import GraphicsLayer from "@arcgis/core/layers/GraphicsLayer";
import GeoJSONLayer from "@arcgis/core/layers/GeoJSONLayer";
import ElevationLayer from "@arcgis/core/layers/ElevationLayer";
import FeatureLayer from "@arcgis/core/layers/FeatureLayer";

// import earcut from 'earcut';

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



export async function createDesigns(model): Promise<void> {
    let basePath: Polyline | undefined = undefined;
    let chartData: any[] = [];

    if (model.selectedDijkvakField) {
        console.log("do stuff here...")

        // Use Promise.all() for parallel processing
        const designPromises = model.graphicsLayerLine.graphics.items
            .filter(graphic => graphic.attributes[model.selectedDijkvakField])
            .map(graphic => {
                const dijkvakValue = graphic.attributes[model.selectedDijkvakField];
                return createDesign(model, graphic.geometry, model.allChartData[dijkvakValue], dijkvakValue);
            });

        await Promise.all(designPromises);
    } else {
        basePath = model.graphicsLayerLine.graphics.items[0].geometry;
        chartData = model.chartData;
        await createDesign(model, basePath, chartData, "default");
    }
}

export async function createDesign(model, basePath, chartData, dijkvak): Promise<void> {
    console.log(basePath, "Base path geometry");

    // Add null checks at the beginning
    if (!basePath) {
        console.error("Base path is null or undefined");
        return;
    }

    if (!chartData || chartData.length === 0) {
        console.error("Chart data is null, undefined, or empty");
        return;
    }

    if (!basePath.spatialReference) {
        console.error("Base path has no spatial reference");
        return;
    }

    // Clear previous meshes for this design
    model.meshes = [];

    let offsetGeometries = []

    // RD New spatial reference (EPSG:28992)
    const rdNewSpatialRef = new SpatialReference({ wkid: 28992 });

    // Ensure projection module is loaded
    await projection.load();

    // Use Promise.all() to process all chart data in parallel
    const offsetPromises = chartData.map(async (row) => {
        try {
            const offsetDistance = row.afstand || 0;

            // Project to RD New for accurate planar offset
            const projectedLine = projection.project(basePath, rdNewSpatialRef) as Polyline;

            if (!projectedLine) {
                console.warn(`Failed to project line for row:`, row);
                return null;
            }

            // Apply planar offset in RD New (very accurate for Netherlands)
            const offsetLineRD = geometryEngine.offset(projectedLine, offsetDistance, "meters", "round") as Polyline;

            if (!offsetLineRD) {
                console.warn(`Failed to create offset for distance ${offsetDistance}:`, row);
                return null;
            }

            // Project back to Web Mercator
            const offsetLine = projection.project(offsetLineRD, SpatialReference.WebMercator) as Polyline;

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
                        type: "simple-line",
                        style: "solid",
                        color: "grey",
                        width: 1,
                    } as __esri.SimpleLineSymbolProperties,
                });

                model.graphicsLayerTemp.add(offsetGraphic);

                if (row.locatie) {
                    return { locatie: row.locatie, geometry: offsetGraphic.geometry };
                } else {
                    console.log("Row name is missing in the data.", row);
                    return null;
                }
            }
        } catch (error) {
            console.error(`Error processing row:`, row, error);
            return null;
        }
        return null;
    });

    // Wait for all offset operations to complete
    const offsetResults = await Promise.all(offsetPromises);

    // Build offsetGeometries object from results, filtering out null values
    offsetResults.forEach(result => {
        if (result?.locatie && result?.geometry) {
            offsetGeometries[result.locatie] = result.geometry;
        }
    });

    console.log("Offset geometries created:", Object.keys(offsetGeometries));

    // Only proceed if we have valid geometries
    if (Object.keys(offsetGeometries).length === 0) {
        console.warn("No valid offset geometries created");
        return;
    }

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

    // console.log(model.uniqueParts, "Unique parts");

    const merged = meshUtils.merge(model.meshes);
    // union polygons first?
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

    // console.log("Elevation sampler created:", elevationSampler);

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



    // console.log("All points processed:", pointCoordsForVolume);

    if (pointCoordsForVolume.length === 0) {
        console.warn("No points were processed. Ensure the mesh geometries and grid size are correct.");
        return;
    }

    // Query ground elevations for all points
    const multipointForGround = new Multipoint({
        points: groundPoints,
        spatialReference: SpatialReference.WebMercator
    });



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

    // const symbol = {
    //     type: "mesh-3d",
    //     symbolLayers: [{ type: "fill" }]
    // };

    model.meshes.push(mesh);

    // graphicsLayerTemp.add(new Graphic({ geometry: mesh, symbol, attributes: { footprint: polygon } }));
}


// functions for debugging with earcut
// function ringArea(ring) {
//   let area = 0;
//   for (let i = 0; i < ring.length; i++) {
//     const [x1, y1] = ring[i];
//     const [x2, y2] = ring[(i + 1) % ring.length];
//     area += (x1 * y2 - x2 * y1);
//   }
//   return area / 2;
// }
// function createMeshFromPolygon(model, polygon, textureUrl = null) {
//     const rings = polygon.rings;
//     const vertices2D = [];
//     const vertices3D = [];
//     const holes = [];
//     let vertexCount = 0;

//     rings.forEach((ring, i) => {
//         console.log(`Ring ${i}, raw coords:`, ring);

//         const area = ringArea(ring);
//         console.log(`Ring ${i} area:`, area);

//         // Fix winding: outer CCW, holes CW
//         const shouldReverse = (i === 0 && area < 0) || (i > 0 && area > 0);
//         const correctedRing = shouldReverse ? [...ring].reverse() : ring;

//         if (i > 0) {
//             holes.push(vertexCount);
//         }

//         correctedRing.forEach(v => {
//             vertices2D.push(v[0], v[1]);
//             vertices3D.push(v[0], v[1], v[2] ?? 0);
//             vertexCount++;
//         });
//     });

//     console.log("Vertices2D:", vertices2D);
//     console.log("Vertices3D:", vertices3D);
//     console.log("Holes:", holes);

//     const triangles = earcut(vertices2D);
//     console.log("Earcut triangles:", triangles);

//     // CREATE TRIANGLE GRAPHICS FOR VISUALIZATION
//     createTriangleGraphics(model, polygon, { triangles, vertices2D, vertices3D });

//     const mesh = new Mesh({
//         spatialReference: polygon.spatialReference,
//         vertexAttributes: { position: vertices3D },
//         components: [{ faces: triangles }]
//     });

//     const symbol = {
//         type: "mesh-3d",
//         symbolLayers: [{
//             type: "fill",
//             material: textureUrl
//                 ? { color: "white", texture: { url: textureUrl } }
//                 : { color: "blue" }
//         }]
//     };

//     model.meshes.push(mesh);
// }

function createPolygonBetween(model, nameA, nameB, offsetGeometries) {
    const geomA = offsetGeometries[nameA];
    const geomB = offsetGeometries[nameB];
    if (!geomA || !geomB) {
        console.warn(`Could not find lines for ${nameA} and/or ${nameB}`);
        return;
    }

    // part for graphiclayers
    const pathAtotal = geomA.paths[0];
    const pathBtotal = geomB.paths[0].slice().reverse();
    let ring = pathAtotal.concat(pathBtotal);
    ring.push(pathAtotal[0]);

    let ring2d = ring.map(point => [point[0], point[1]]);

    const polygon3d = new Polygon({
        rings: [ring],
        spatialReference: geomA.spatialReference
    });

    const polygon2d = new Polygon({
        rings: [ring2d],
        spatialReference: geomA.spatialReference
    });

    const partName = `${nameA}-${nameB}`;

    const graphics2D = new Graphic({
        geometry: polygon2d,
        attributes: { name: partName }
    });

    const graphic3d = new Graphic({
        geometry: polygon3d,
        attributes: { name: partName }
    });

    model.graphicsLayerTemp.add(graphic3d);

    model.designLayer2D.applyEdits({
        addFeatures: [graphics2D]
    }).catch((error) => {
        console.error("Error adding 2D polygon to design layer:", error);
    });

    // part for meshes, taking care of proper triangulation
    const pathAforMesh = geomA.paths[0];
    const pathBforMesh = geomB.paths[0];

    // Make sure both paths have the same number of vertices
    const minLength = Math.min(pathAforMesh.length, pathBforMesh.length);
    const trimmedPathA = pathAforMesh.slice(0, minLength);
    const trimmedPathB = pathBforMesh.slice(0, minLength);

    // Create segments by connecting corresponding vertex pairs
    for (let i = 0; i < minLength - 1; i++) {
        // Create a quad (4-sided polygon) from two consecutive vertex pairs
        const quad = [
            trimmedPathA[i],       // Vertex i on line A
            trimmedPathA[i + 1],   // Vertex i+1 on line A  
            trimmedPathB[i + 1],   // Vertex i+1 on line B
            trimmedPathB[i],       // Vertex i on line B
            trimmedPathA[i]        // Close the polygon
        ];

        const segmentPolygon = new Polygon({
            rings: [quad],
            spatialReference: geomA.spatialReference
        });

        // const partName = `${nameA}-${nameB}`;

        // const graphic3d = new Graphic({
        //     geometry: segmentPolygon,
        //     attributes: { name: partName }
        // });

        // model.graphicsLayerTemp.add(graphic3d);

        // // Create 2D version
        // const ring2d = quad.map(point => [point[0], point[1]]);
        // const polygon2d = new Polygon({
        //     rings: [ring2d],
        //     spatialReference: geomA.spatialReference
        // });

        // const graphics2D = new Graphic({
        //     geometry: polygon2d,
        //     attributes: { name: partName }
        // });

        // model.designLayer2D.applyEdits({
        //     addFeatures: [graphics2D]
        // }).catch((error) => {
        //     console.error("Error adding 2D polygon to design layer:", error);
        // });

        // model.uniqueParts.push(partName);

        // Each quad will have simple, predictable triangulation
        createMeshFromPolygon(model, segmentPolygon, null);
    }
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

export function initializeChart(model, activeTab, chartContainerRef, seriesRef): () => void {
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
    seriesRef.current = series

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
export function initializeCrossSectionChart(model, crossSectionChartContainerRef, refs: { chartSeriesRef: any; meshSeriesRef: any; userSeriesRef: any }): () => void {
    const { chartSeriesRef, meshSeriesRef, userSeriesRef } = refs;

    if (!model.crossSectionChartData || !crossSectionChartContainerRef?.current) {
        console.log(model.crossSectionChartData, crossSectionChartContainerRef?.current, "Chart not initialized");
        return
    }


    model.crossSectionChartRoot = am5.Root.new(crossSectionChartContainerRef.current);
    const root = model.crossSectionChartRoot as am5.Root;
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

    const elevationSeries = chart.series.push(
        am5xy.LineSeries.new(root, {
            name: "Hoogte vs Afstand",
            xAxis: xAxis as any,
            yAxis: yAxis as any,
            valueYField: "hoogte",
            valueXField: "afstand",
            tooltip: am5.Tooltip.new(root, {
                labelText: "Grond hoogte: {valueY}",
            }),
            stroke: am5.color(0xff9900),
        })
    );

    elevationSeries.data.setAll(model.crossSectionChartData);
    chartSeriesRef.current = elevationSeries

    elevationSeries.strokes.template.setAll({
        strokeWidth: 3,
    });

    const meshSeries = chart.series.push(
        am5xy.LineSeries.new(root, {
            name: "Mesh Hoogte vs Afstand",
            xAxis: xAxis as any,
            yAxis: yAxis as any,
            valueYField: "hoogte",
            valueXField: "afstand",
            tooltip: am5.Tooltip.new(root, {
                labelText: "Ontwerp hoogte: {valueY}",
            }),
            stroke: am5.color(0x888888)
        })
    );

    if (model.meshSeriesData?.length) {
        meshSeries.data.setAll(model.meshSeriesData);
        console.log(model.meshSeriesData, "Mesh series data has been set");
    }

    meshSeriesRef.current = meshSeries;
    meshSeries.strokes.template.setAll({
        strokeWidth: 3,
    });

    const userSeries = chart.series.push(
        am5xy.LineSeries.new(root, {
            name: "User Drawn Line",
            xAxis: xAxis as any,
            yAxis: yAxis as any,
            valueYField: "hoogte",
            valueXField: "afstand",
            stroke: am5.color(0x800080), // purple
            tooltip: am5.Tooltip.new(root, {
                labelText: "{valueY}",
            }),
        })
    );

    // Add bullets (markers) at each clicked point
    userSeries.bullets.push((root, series, dataItem) => (
        am5.Bullet.new(root, {
            sprite: am5.Circle.new(root, {
                radius: 6,
                fill: am5.color(0x800080), // purple fill
                stroke: am5.color(0xffffff),
                strokeWidth: 2,
            })
        })
    ));

    userSeries.strokes.template.setAll({
        stroke: am5.color(0x800080), // purple
        strokeWidth: 2,
    });

    function updateSlopeLabels() {
        // Clear old labels
        model.slopeLabels.forEach(label => label.dispose());
        model.slopeLabels = [];

        const points = model.userLinePoints;
        if (!points || points.length < 2) return;

        for (let i = 1; i < points.length; i++) {
            const p1 = points[i - 1];
            const p2 = points[i];

            const deltaX = p2.afstand - p1.afstand;
            const deltaY = p2.hoogte - p1.hoogte;

            let slopeRatio;
            if (deltaY === 0) {
                slopeRatio = "∞";
            } else {
                slopeRatio = (Math.abs(deltaX / deltaY)).toFixed(2);
            }

            const labelText = `1:${slopeRatio}`;

            // Position label halfway between points
            const midX = (p1.afstand + p2.afstand) / 2;
            const midY = (p1.hoogte + p2.hoogte) / 2;

            console.log(midX, midY, "Midpoint coordinates for slope label");

            const label = chart.plotContainer.children.push(
                am5.Label.new(root, {
                    text: labelText,
                    x: xAxis.get("renderer").positionToCoordinate(xAxis.valueToPosition(midX)),
                    y: yAxis.get("renderer").positionToCoordinate(yAxis.valueToPosition(midY)),
                    centerX: am5.p50,
                    centerY: am5.p50,
                    background: am5.Rectangle.new(root, {
                        fill: am5.color(0xffffff),
                        fillOpacity: 0.7
                    }),
                    paddingLeft: 2,
                    paddingRight: 2,
                    paddingTop: 1,
                    paddingBottom: 1,
                    fontSize: 14
                })
            );
            console.log(label, "Slope label created: ", labelText)

            model.slopeLabels.push(label);
        }
    }
    chart.plotContainer.events.on("click", (ev) => {
        // Convert pixel coordinates to axis values
        const point = chart.plotContainer.toLocal(ev.point);
        const afstand = xAxis.positionToValue(xAxis.coordinateToPosition(point.x));
        const hoogte = yAxis.positionToValue(yAxis.coordinateToPosition(point.y));

        // Add the new point to the array
        model.userLinePoints.push({ afstand, hoogte });
        // model.setUserLinePoints([...userLinePoints]); // For React state, or just update the array if not using React

        // Update the series data
        userSeries.data.setAll(model.userLinePoints);
        updateSlopeLabels();
    });

    chart.events.on("boundschanged", () => {
        updateSlopeLabels();
    });

    xAxis.on("start", () => {
        console.log("X Axis end event triggered");
        updateSlopeLabels();
    });

    yAxis.on("start", () => {
        updateSlopeLabels();
    });

    userSeries.strokes.template.setAll({
        stroke: am5.color(0x00cc00),
        strokeWidth: 2,
    });

    const clearButton = chart.children.push(
        am5.Button.new(root, {
            label: am5.Label.new(root, { text: "Verwijder taludlijn", fontSize: 14 }),
            x: 50,
            y: 35,
            centerX: am5.p0,
            centerY: am5.p0,
            // paddingLeft: 25,
            // paddingRight: 25,
            // paddingTop: 5,
            // paddingBottom: 5,
            // background: am5.RoundedRectangle.new(root, {
            //     fill: am5.color(0xffcccc),
            //     fillOpacity: 1,
            //     cornerRadiusTL: 8,
            //     cornerRadiusTR: 8,
            //     cornerRadiusBL: 8,
            //     cornerRadiusBR: 8,
            // }),
        })
    );

    clearButton.events.on("click", () => {
        model.userLinePoints = [];
        userSeries.data.setAll([]);
        // Remove slope labels
        if (model.slopeLabels) {
            model.slopeLabels.forEach(label => label.dispose());
            model.slopeLabels = [];
        }
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

                })
            })

        } else {
            console.warn("No features found in the selected feature layer.");
        }
    }).catch((error) => {
        console.error("Error querying feature layer:", error);
    })

}

export function cleanFeatureLayer(layer) {
    layer.queryObjectIds().then((objectIds) => {
        if (objectIds.length === 0) {
            console.log("No features to delete.");
            return;
        }
        const deletes = objectIds.map(id => ({
            objectId: id
        }));

        layer.applyEdits({
            deleteFeatures: deletes
        }).catch((error) => {
            console.error("Error deleting features:", error);
        });
    });
}


export async function createCrossSection(model) {
    model.messages.commands.ui.displayNotification.execute({

        title: "Cross Section",
        message: "Klik op de kaart om een dwarsprofiel te tekenen. Deze tool is in ontwikkeling.",
        type: "success",
    })
    model.startDrawingLine(model.graphicsLayerCrossSection).then(() => { // set interval dynamically?
        getPointsOnLine(model.graphicsLayerCrossSection.graphics.items[0].geometry, 0.1).then((offsetLocations) => {
            console.log(offsetLocations, "Offset locations for cross section");
            const sRef = model.graphicsLayerCrossSection.graphics.items[0].geometry.spatialReference;
            const promises = offsetLocations.map(loc =>
                getPointAlongLine(model.graphicsLayerCrossSection.graphics.items[0].geometry.paths[0], loc, sRef)
            );

            Promise.all(promises).then(async pointGraphics => {
                console.log(pointGraphics, "Point graphics for cross section");
                const multipoint = new Multipoint({
                    hasM: true,
                    points: pointGraphics.map(g => {
                        const { x, y } = g.geometry as Point;
                        const offset = g.attributes?.offset ?? 0;
                        return [x, y, undefined, offset]; // [x, y, z, m]
                    }),
                    spatialReference: model.graphicsLayerCrossSection.graphics.items[0].geometry.spatialReference
                });
                console.log(pointGraphics, "Point graphics for cross section");
                console.log(multipoint, "Multipoint for cross section");

                const elevationResult = await model.elevationLayer.queryElevation(multipoint, { returnSampleInfo: true });

                model.crossSectionChartData = elevationResult.geometry.points.map((point, index) => ({
                    afstand: point[3], // m value
                    hoogte: point[2]
                }));


                model.crossSectionPanelVisible = true;


                console.log("Elevation query result:", elevationResult);

                if (model.meshes.length > 0) {

                    let elevationSampler = await meshUtils.createElevationSampler(
                        model.mergedMesh, {
                        noDataValue: -999
                    }
                    );



                    const meshElevationResult = elevationSampler.queryElevation(multipoint)
                    console.log("Mesh elevation result:", meshElevationResult);
                    if ("points" in meshElevationResult && Array.isArray(meshElevationResult.points)) {
                        model.meshSeriesData = meshElevationResult.points
                            .filter(point => point[2] !== -999)
                            .map((point, index) => ({
                                afstand: point[3], // m value
                                hoogte: point[2]
                            }));
                        console.log("Mesh series data:", model.meshSeriesData);
                    } else {
                        model.meshSeriesData = [];
                        console.warn("meshElevationResult does not have a 'points' property or is not an array.", meshElevationResult);
                    }

                    console.log("Mesh elevation result:", meshElevationResult);


                }

                model.messages.commands.ui.displayNotification.execute({

                    title: "Cross Section",
                    message: "Dwarsprofiel punten opgehaald en hoogtes berekend, deze worden straks getoond in de grafiek. Deze tool is in ontwikkeling.",
                    type: "success",
                });
            });

            // model.crossSectionLocations = offsetLocations;
            // model.graphicsLayerTemp.removeAll();
        });
    });
}

// code for creating offset locations based on a start offset, segment length, step size, and segment number --> move to separate file if needed
export function createOffsetLocations(
    startOffset: number,
    segmentLength: number,
    stepSize: number,
    segmentNumber: number
) {
    const locations = [];
    let iterations = Math.floor(segmentLength / stepSize);
    let offset = startOffset;
    let offsetInSegment = 0;
    for (let i = 0; i < iterations; i++) {
        locations.push({
            offset,
            offsetInSegment,
            segment: segmentNumber,
        });
        offset += stepSize;
        offsetInSegment += stepSize;
    }
    return locations;
}

export function getPointsOnLine(profileLine: any, intervalSize: number): Promise<any[]> {
    return new Promise((resolve, reject) => {
        try {
            const path = profileLine.paths[0];
            const lineSegments = path.length - 1;
            let totalLength = 0;
            let startDistance = 0;
            let offsetLocations: any[] = [];

            for (let step = 0; step < lineSegments; step++) {
                const [xStart, yStart] = path[step];
                const [xEnd, yEnd] = path[step + 1];

                const lineSegment = new Polyline({
                    hasZ: false,
                    hasM: false,
                    paths: [
                        [
                            [xStart, yStart],
                            [xEnd, yEnd],
                        ],
                    ],
                    spatialReference: profileLine.spatialReference,
                });

                let segmentLength = Math.round(geometryEngine.geodesicLength(lineSegment, "meters"));
                if (segmentLength % 2 !== 0) segmentLength += 1;

                totalLength += segmentLength;

                // Add offset locations for this segment
                offsetLocations = offsetLocations.concat(
                    createOffsetLocations(startDistance, segmentLength, intervalSize, step)
                );
                startDistance += segmentLength;
            }
            //   console.log(offsetLocations, "Offset locations");
            resolve(offsetLocations);
        } catch (error) {
            reject(error);
        }
    });
}

export function getPointAlongLine(
    paths: number[],
    offsetLocation: { offset: number; offsetInSegment: number; segment: number },
    spatialReference: __esri.SpatialReference
): Promise<__esri.Graphic> {
    return new Promise((resolve, reject) => {
        try {
            const x1 = paths[offsetLocation.segment][0];
            const y1 = paths[offsetLocation.segment][1];
            const x2 = paths[offsetLocation.segment + 1][0];
            const y2 = paths[offsetLocation.segment + 1][1];

            const lineSegment = new Polyline({
                hasZ: false,
                hasM: false,
                paths: [
                    [
                        [x1, y1],
                        [x2, y2],
                    ],
                ],
                spatialReference,
            });

            const pathDistancePlanar = geometryEngine.planarLength(lineSegment, "meters");
            const pathDistanceGeodesic = geometryEngine.geodesicLength(lineSegment, "meters");
            const planarToGeodesic = pathDistancePlanar / pathDistanceGeodesic;

            let distanceDiff = offsetLocation.offsetInSegment * planarToGeodesic;

            const angle = Math.atan2(y2 - y1, x2 - x1);
            const x3 = distanceDiff * Math.cos(angle);
            const y3 = distanceDiff * Math.sin(angle);

            const point = new Point({
                x: x1 + x3,
                y: y1 + y3,
                m: offsetLocation.offset,
                spatialReference,
            });

            const defaultPointSymbol = {
                type: "simple-marker",
                color: [226, 119, 40, 0],
                outline: {
                    color: [255, 255, 255, 0],
                    width: 1,
                },
            };

            const pointGraphic = new Graphic({
                geometry: point,
                symbol: defaultPointSymbol,
                attributes: {
                    offset: offsetLocation.offset,
                },
            });

            resolve(pointGraphic);
        } catch (error) {
            reject(error);
        }
    });
}

function createTriangleGraphics(model, polygon, triangulationData) {
    const { triangles, vertices2D, vertices3D } = triangulationData;
    
    // Create graphics for each triangle
    for (let i = 0; i < triangles.length; i += 3) {
        const a = triangles[i];
        const b = triangles[i + 1];
        const c = triangles[i + 2];

        // Get 3D coordinates for triangle vertices
        const vertex1 = [vertices3D[a * 3], vertices3D[a * 3 + 1], vertices3D[a * 3 + 2] || 0];
        const vertex2 = [vertices3D[b * 3], vertices3D[b * 3 + 1], vertices3D[b * 3 + 2] || 0];
        const vertex3 = [vertices3D[c * 3], vertices3D[c * 3 + 1], vertices3D[c * 3 + 2] || 0];

        // Create triangle polygon
        const trianglePolygon = new Polygon({
            rings: [[vertex1, vertex2, vertex3, vertex1]], // Close the ring
            spatialReference: polygon.spatialReference
        });

        // Calculate triangle area to color code them
        const area = Math.abs(geometryEngine.planarArea(trianglePolygon, "square-meters"));

        // Color based on area - red for very small triangles, green for normal ones
        let fillColor = [0, 255, 0, 0.3]; // Green with transparency
        let outlineColor = [0, 255, 0, 1];

        if (area < 1.0) { // Very small triangles in red
            fillColor = [255, 0, 0, 0.5];
            outlineColor = [255, 0, 0, 1];
        } else if (area < 5.0) { // Small triangles in yellow
            fillColor = [255, 255, 0, 0.4];
            outlineColor = [255, 255, 0, 1];
        }

        const triangleGraphic = new Graphic({
            geometry: trianglePolygon,
            symbol: {
                type: "simple-fill",
                color: fillColor,
                outline: {
                    color: outlineColor,
                    width: 1
                }
            } as __esri.SimpleFillSymbolProperties,
            attributes: {
                triangleIndex: Math.floor(i / 3),
                area: area.toFixed(2),
                vertices: `${a}, ${b}, ${c}`
            }
        });

        model.graphicsLayerTemp.add(triangleGraphic);
    }

    // Add vertex markers to see the actual points
    for (let i = 0; i < vertices3D.length; i += 3) {
        const point = new Point({
            x: vertices3D[i],
            y: vertices3D[i + 1],
            z: vertices3D[i + 2] || 0,
            spatialReference: polygon.spatialReference
        });

        const pointGraphic = new Graphic({
            geometry: point,
            symbol: {
                type: "simple-marker",
                color: [0, 0, 255, 0.8], // Blue points
                size: 6,
                outline: {
                    color: [255, 255, 255, 1],
                    width: 1
                }
            } as __esri.SimpleMarkerSymbolProperties,
            attributes: {
                vertexIndex: Math.floor(i / 3)
            }
        });

        model.graphicsLayerTemp.add(pointGraphic);
    }

    console.log(`Created ${triangles.length / 3} triangle graphics and ${vertices3D.length / 3} vertex markers`);
}