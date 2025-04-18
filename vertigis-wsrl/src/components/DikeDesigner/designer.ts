
import type {
    ApplyDesignerSettingsCallback,
    ComponentModelDesignerSettings,
    DesignerSettings,
    GetDesignerSettingsCallback,
    GetDesignerSettingsSchemaCallback,
    Setting,
    SettingsSchema,
} from "@vertigis/web/designer";
import {
    applyComponentModelDesignerSettings,
    getComponentModelDesignerSettings,
    getComponentModelDesignerSettingsSchema,
} from "@vertigis/web/designer";

import type { DikeDesignerModelProperties } from "./DikeDesignerModel";
import type DikeDesignerModel from "./DikeDesignerModel";

export interface DikeDesignerSettings extends ComponentModelDesignerSettings {
    elevationLayerUrl?: string;
}

export type SettingsMap = DesignerSettings<DikeDesignerSettings>;

export const applySettings: ApplyDesignerSettingsCallback<DikeDesignerModel, SettingsMap> = async (args) => {
    const { model, settings } = args;
    const { elevationLayerUrl, ...otherSettings } = settings;
    await applyComponentModelDesignerSettings(args);

    const applySettings: Partial<DikeDesignerModelProperties> = otherSettings;

    if (elevationLayerUrl !== undefined) {    
        applySettings.elevationLayerUrl = elevationLayerUrl;
    }

    model.assignProperties(applySettings);
};

export const getSettings: GetDesignerSettingsCallback<DikeDesignerModel, SettingsMap> = async (args) => {
    const { model } = args;
    const { elevationLayerUrl } = model;
    return {
        ...await getComponentModelDesignerSettings(args),
        elevationLayerUrl
    };
};

export const getSettingsSchema: GetDesignerSettingsSchemaCallback<DikeDesignerModel, SettingsMap> = async (args) => {
    const baseSchema = await getComponentModelDesignerSettingsSchema(args);
    (baseSchema.settings[0].settings as Setting<DikeDesignerSettings>[]) = (
        baseSchema.settings[0].settings as Setting<DikeDesignerSettings>[]
    ).concat([

        {
            id: "elevationLayerUrl",
            type: "text",            
            description: "The url for the elevation layer.",
            displayName: "Elevation Layer URL",
        },
    ]);

    const schema: SettingsSchema<DikeDesignerSettings> = {
        ...baseSchema,
        settings: [...baseSchema.settings],
    };
    return schema;
};
