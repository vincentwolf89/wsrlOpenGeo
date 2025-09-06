import type { LibraryRegistry } from "@vertigis/web/config";

import ElevationExaggerator from "./ElevationExaggerator";
import ElevationExaggeratorModel from "./ElevationExaggeratorModel";


export { default } from "./ElevationExaggerator";
export { ElevationExaggeratorModel };

export function registerElevationExaggeratorComponent(registry: LibraryRegistry) {
    registry.registerComponent({
        // Show in the `map` category of the component toolbox.
        category: "map",
        iconId: "station-locator",
        name: "elevation-exaggerator",
        namespace: "vertigis-wsrl",
        getComponentType: () => ElevationExaggerator,
        itemType: "elevation-exaggerator-model",
        title: "Elevation Exaggerator",
    });

    registry.registerModel({
        getModel: (config) => new ElevationExaggeratorModel(config),
        itemType: "elevation-exaggerator-model",
    });
}
