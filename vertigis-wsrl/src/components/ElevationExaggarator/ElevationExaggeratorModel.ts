/* eslint-disable @typescript-eslint/no-unnecessary-type-assertion */
/* eslint-disable @typescript-eslint/no-unsafe-argument */
import type {
    ComponentModelProperties,
    PropertyDefs,
} from "@vertigis/web/models";
import {
    ComponentModelBase,
    serializable,
} from "@vertigis/web/models";
import BaseElevationLayer from "esri/layers/BaseElevationLayer";
import ElevationLayer from "esri/layers/ElevationLayer"


export interface ElevationExaggeratorModelProperties extends ComponentModelProperties {
    elevationLayerUrl?: string;
}

@serializable
export default class ElevationExaggeratorModel extends ComponentModelBase<ElevationExaggeratorModelProperties> {
    map: any;
    view: any;

    elevationLayerUrl: ElevationExaggeratorModelProperties["elevationLayerUrl"];

    exaggeration: number = 1;

    processChange(): void {

            const  newGround = this.createNewElevation(this.exaggeration);
            this.map.ground.layers = [new newGround];
    }

    createNewElevation(factor: number): typeof BaseElevationLayer {
        class ExaggeratedElevationLayer extends BaseElevationLayer {
                private _elevation: ElevationLayer;
                

                async load() {
                    this._elevation = new ElevationLayer({
                        url: "//elevation3d.arcgis.com/arcgis/rest/services/WorldElevation3D/Terrain3D/ImageServer"
                    });
                    await this.addResolvingPromise(this._elevation.load());
                }

                async fetchTile(level: number, row: number, col: number, options: any) {
                    const data = await this._elevation.fetchTile(level, row, col, options as any);
                    const exaggeration = factor;
                    for (let i = 0; i < data.values.length; i++) {
                        if (data.values[i] !== data.noDataValue) {
                            data.values[i] *= exaggeration;
                        }
                    }
                    return data;
                }
            }
            return ExaggeratedElevationLayer
    }

    protected override _getSerializableProperties(): PropertyDefs<ElevationExaggeratorModelProperties> {
        return {
            ...super._getSerializableProperties(),
            elevationLayerUrl: {
                serializeModes: ["initial"],
                default: "//elevation3d.arcgis.com/arcgis/rest/services/WorldElevation3D/Terrain3D/ImageServer",
            },
        };
    }

    protected async _onInitialize(): Promise<void> {
        await super._onInitialize();

        this.messages.events.map.initialized.subscribe(async (map) => {
            console.log("Map initialized:", map);
            this.map = map.maps.map;
            this.view = map.maps["view"];
            const newGround = this.createNewElevation(this.exaggeration);

            this.map.ground.layers = [new newGround];

            // https://developers.arcgis.com/javascript/latest/sample-code/layers-custom-elevation-exaggerated/



        });
    }
}
