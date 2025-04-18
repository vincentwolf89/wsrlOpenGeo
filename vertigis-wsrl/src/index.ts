import type { LibraryRegistry } from "@vertigis/web/config";
import type { GetDesignerSettingsSchemaArgs } from "@vertigis/web/designer";

import DikeDesigner, { DikeDesignerModel } from "./components/DikeDesigner";


const LAYOUT_NAMESPACE = "vertigis-wsrl";

const getDikeDesigner = () => import("./components/DikeDesigner");

export default function (registry: LibraryRegistry): void {
    registry.registerComponent({
        // Show in the `map` category of the component toolbox.
        category: "map",
        iconId: "station-locator",
        name: "dike-designer",
        namespace: LAYOUT_NAMESPACE,
        getComponentType: () => DikeDesigner,
        itemType: "dike-designer-model",
        title: "Dike designer",
        getDesignerSettings: async (
            args: GetDesignerSettingsSchemaArgs<DikeDesignerModel, "">
        ) => (await getDikeDesigner()).getSettings(args),
        applyDesignerSettings: async (args) =>
            (await getDikeDesigner()).applySettings(args),
        getDesignerSettingsSchema: async (
            args: GetDesignerSettingsSchemaArgs<DikeDesignerModel, "">
        ) => (await getDikeDesigner()).getSettingsSchema(args),
    });
    registry.registerModel({
        getModel: config => new DikeDesignerModel(config),
        itemType: "dike-designer-model",
    });
}
