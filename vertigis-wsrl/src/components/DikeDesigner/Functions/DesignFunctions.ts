/* eslint-disable prefer-const */
/* eslint-disable @typescript-eslint/no-floating-promises */
/* eslint-disable @typescript-eslint/no-unsafe-argument */
/* eslint-disable @typescript-eslint/no-unused-vars */
/* eslint-disable @typescript-eslint/consistent-type-imports */
/* eslint-disable import/order */

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
export async function createDesign(model) {
    // if (model.graphicsLayerLine.graphics.length === 0) {
    //     alert("Please sketch a line before uploading an Excel file.");
    //     return;
    // }
    model.meshes = [];
    const basePath = model.graphicsLayerLine.graphics.items[0].geometry;
    console.log(basePath, "Base path geometry");


    // if (!basePath || !basePath.paths || basePath.paths.length === 0) {
    //     alert("No valid line found for offset calculations.");
    //     return;
    // }

    await model.chartData.forEach(row => {
        const offsetDistance = (row.afstand || 0);
        const offsetLine = geometryEngine.offset(basePath, offsetDistance) as Polyline;

        if (offsetLine) {
            const elevation = row.hoogte || 0;
            const updatedPaths = offsetLine.paths.map(path =>
                path.map(coord => [coord[0], coord[1], elevation])
            );

            const offsetGraphic = new Graphic({
                geometry: new Polyline({
                    paths: updatedPaths,
                    spatialReference: SpatialReference.WebMercator
                }),
                symbol: {
                    type: "simple-line", // SimpleLineSymbol type
                    style: "solid",
                    color: "grey",
                    width: 1
                } as __esri.SimpleLineSymbolProperties
            });

            model.graphicsLayerTemp.add(offsetGraphic);



            if (row.locatie) {
                model.offsetGeometries[row.locatie] = offsetGraphic.geometry;
            } else {
                console.log("Row name is missing in the data.", row);
            }
        }
    });

    console.log(model.offsetGeometries, "Offset geometries");

    createPolygonBetween(model, "buitenkruin", "binnenkruin", [128, 0, 0, 0.9]);

    let containsBerm = model.chartData.some(row => row.locatie?.toLowerCase().includes("berm"));

    if (containsBerm) {
        createPolygonBetween(model, "buitenkruin", "bovenkant_buitenberm", [50, 205, 50, 0.9]);
        createPolygonBetween(model, "binnenkruin", "bovenkant_binnenberm", [50, 205, 50, 0.9]);
        createPolygonBetween(model, "bovenkant_buitenberm", "onderkant_buitenberm", [50, 205, 50, 0.9]);
        createPolygonBetween(model, "onderkant_buitenberm", "buitenteen", [50, 205, 50, 0.9]);
        createPolygonBetween(model, "bovenkant_binnenberm", "onderkant_binnenberm", [50, 205, 50, 0.9]);
        createPolygonBetween(model, "onderkant_binnenberm", "binnenteen", [50, 205, 50, 0.9]);
    } else {
        createPolygonBetween(model, "buitenkruin", "binnenkruin", [128, 0, 0, 0.9]);
        createPolygonBetween(model, "buitenkruin", "buitenteen", [50, 205, 50, 0.9]);
        createPolygonBetween(model, "binnenkruin", "binnenteen", [50, 205, 50, 0.9]);
    }

    const merged = meshUtils.merge(model.meshes)
    const mergedGraphic = new Graphic({
        geometry: merged,
        symbol: {
            type: "mesh-3d",
            symbolLayers: [{ type: "fill" }]
        } as __esri.Symbol3DLayerProperties,
    });
    model.graphicsLayerTemp.add(mergedGraphic);
    model.mergedMesh = merged
    model.meshGraphic = mergedGraphic;






    //     };

    // }
}

export async function calculateVolume(model) {
    const gridSize = model.gridSize;

    const elevationSampler = await meshUtils.createElevationSampler(model.mergedMesh, model.mergedMesh.extent);
    const extent = model.meshGraphic.geometry.extent;

    const pointCoordsForVolume = [];
    const groundPoints = [];

    for (let x = extent.xmin; x <= extent.xmax; x += gridSize) {
        for (let y = extent.ymin; y <= extent.ymax; y += gridSize) {
            const point = new Point({
                x: x as number,
                y: y as number,
                spatialReference: { wkid: 3857 }
            });

            // Query the elevation at the point
            const elevation = elevationSampler.elevationAt(point.x, point.y);
            if (elevation) {
                point.z = elevation;

                // Add the point to the volume calculation
                pointCoordsForVolume.push([point.x, point.y, point.z]);

                // Add the point to the ground elevation query
                groundPoints.push(point);
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
        points: groundPoints.map(p => [p.x, p.y]),
        spatialReference: { wkid: 3857 }
    });

    const groundResult = await model.elevationLayer.queryElevation(multipointForGround, { returnSampleInfo: true });
    console.log("Ground elevation query result:", groundResult);

    let totalVolumeDifference = 0;
    let excavationVolume= 0;
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
function createPolygonBetween(model, nameA, nameB, fillColor) {
    console.log(nameA, nameB, model.offsetGeometries, "createPolygonBetween function called");
    const geomA = model.offsetGeometries[nameA];
    const geomB = model.offsetGeometries[nameB];
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

    // featureLayerDesign.applyEdits({
    //     addFeatures: [graphic]
    // });

    createMeshFromPolygon(model, polygon, null);
}