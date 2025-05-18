import * as geometryEngine from "@arcgis/core/geometry/geometryEngine";
import type FeatureLayer from "@arcgis/core/layers/FeatureLayer";
// import Query from "@arcgis/core/rest/support/Query";


export async function getIntersectingFeatures(model, layerTitle) {

    const layerToQuery = model.map.allLayers.items.find(
        (layer) => layer.title === layerTitle
    ) as FeatureLayer;

    if (!layerToQuery) {
        console.warn("BAG panden layer not found!");
        return [];
    }

    const geometries = model.graphicsLayerTemp.graphics.items.map(g => g.geometry);

    const unionGeometry = geometries.length > 1
        ? geometryEngine.union(geometries as __esri.Geometry[])
        : geometries[0];

    if (!unionGeometry) {
        console.warn("No geometry to query with.");
        return [];
    }

    const query = layerToQuery.createQuery();
    query.returnGeometry = true;
    query.outFields = ["*"];
    query.geometry = unionGeometry;
    query.spatialRelationship = "intersects";

    try {
        const result = await layerToQuery.queryFeatures(query);
        console.log("Intersecting features:", result);
        return result.features;
    } catch (error) {
        console.error("Error querying features:", error);
        return [];
    }
    
}