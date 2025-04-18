
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
    netwerkLayer?: string;
}

export type SettingsMap = DesignerSettings<DikeDesignerSettings>;

export const applySettings: ApplyDesignerSettingsCallback<DikeDesignerModel, SettingsMap> = async (args) => {
    const { model, settings } = args;
    const { netwerkLayer, ...otherSettings } = settings;
    await applyComponentModelDesignerSettings(args);

    const applySettings: Partial<DikeDesignerModelProperties> = otherSettings;

    if (netwerkLayer !== undefined) {    
        applySettings.netwerkLayer = netwerkLayer;
    }

    model.assignProperties(applySettings);
};

export const getSettings: GetDesignerSettingsCallback<DikeDesignerModel, SettingsMap> = async (args) => {
    const { model } = args;
    const { netwerkLayer } = model;
    return {
        ...await getComponentModelDesignerSettings(args),
        netwerkLayer
    };
};

export const getSettingsSchema: GetDesignerSettingsSchemaCallback<DikeDesignerModel, SettingsMap> = async (args) => {
    const baseSchema = await getComponentModelDesignerSettingsSchema(args);
    (baseSchema.settings[0].settings as Setting<DikeDesignerSettings>[]) = (
        baseSchema.settings[0].settings as Setting<DikeDesignerSettings>[]
    ).concat([

        {
            id: "netwerkLayer",
            type: "text",            
            description: "The name of the layer that contains the netwerk.",
            displayName: "Netwerk Layer",
        },
    ]);

    const schema: SettingsSchema<DikeDesignerSettings> = {
        ...baseSchema,
        settings: [...baseSchema.settings],
    };
    return schema;
};
