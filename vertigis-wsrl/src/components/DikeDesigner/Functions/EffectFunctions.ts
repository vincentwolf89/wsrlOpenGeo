import * as geometryEngine from "@arcgis/core/geometry/geometryEngine";
import type FeatureLayer from "@arcgis/core/layers/FeatureLayer";
import Query from "@arcgis/core/rest/support/Query";


export async function getIntersectingFeatures(model, layer) {
    // Get BAG panden layer
    const bagPandenLayer = model.map.allLayers.items.find(
        (layer) => layer.title === "3D BAG WGS"
    ) as FeatureLayer;

    if (!bagPandenLayer) {
        console.warn("BAG panden layer not found!");
        return [];
    }

    // Collect all geometries from the graphics
    const geometries = model.graphicsLayerTemp.graphics.items.map(g => g.geometry);

    // Union all geometries into one (returns null if array is empty)
    const unionGeometry = geometries.length > 1
        ? geometryEngine.union(geometries as __esri.Geometry[])
        : geometries[0];

    if (!unionGeometry) {
        console.warn("No geometry to query with.");
        return [];
    }

    const query = new Query();
    // query.where = "1=1";
    query.returnGeometry = true;
    query.outFields = ["*"]
    query.geometry = unionGeometry;
    query.spatialRelationship = "intersects";

    // Query the layer for intersecting features
    const result = await bagPandenLayer.queryFeatures(query);
    console.log("Intersecting features:", result);

    // Return the intersecting features
    return result.features;
}