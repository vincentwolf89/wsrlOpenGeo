export interface GeoJSONGeometry {
    type: "Point" | "LineString" | "Polygon" | "MultiPoint" | "MultiLineString" | "MultiPolygon" | "GeometryCollection";
    coordinates: any; // Use specific types for each geometry type if needed
}

export interface GeoJSONProperties {
    [key: string]: any; // Define specific properties if known, otherwise allow any key-value pairs
}

export interface GeoJSONFeature {
    type: "Feature";
    geometry: GeoJSONGeometry;
    properties: GeoJSONProperties;
}

export interface GeoJSONFeatureCollection {
    type: "FeatureCollection";
    features: GeoJSONFeature[];
    crs?: {
        type: string;
        properties: {
            name: string;
        };
    };
}