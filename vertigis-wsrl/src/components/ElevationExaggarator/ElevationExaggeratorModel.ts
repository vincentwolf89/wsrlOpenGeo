import ElevationLayer from "esri/layers/ElevationLayer"
import BaseElevationLayer from "esri/layers/BaseElevationLayer";

import type {
    ComponentModelProperties,
    PropertyDefs,
} from "@vertigis/web/models";
import {
    ComponentModelBase,
    serializable,
    importModel,
} from "@vertigis/web/models";


export interface ElevationExaggeratorModelProperties extends ComponentModelProperties {
    buttonName?: string;
    buttonId?: string;
    command?: string;
}

@serializable
export default class ElevationExaggeratorModel extends ComponentModelBase<ElevationExaggeratorModelProperties> {
    map: any;
    view: any;

    toggleON: boolean = false;
    buttonName: ElevationExaggeratorModelProperties["buttonName"];
    buttonId: ElevationExaggeratorModelProperties["buttonId"];
    command: ElevationExaggeratorModelProperties["command"];

    valueText: String = "Temperature";

    processToggle(): void {

        this.toggleON = !this.toggleON;
    }

    protected override _getSerializableProperties(): PropertyDefs<ElevationExaggeratorModelProperties> {
        return {
            ...super._getSerializableProperties(),
            buttonName: {
                serializeModes: ["initial"],
                default: "Label uitvoering",
            },
            buttonId: {
                serializeModes: ["initial"],
                default: "uitvoeringButtonId",
            },
            command: {
                serializeModes: ["initial"],
                default: "layer-service.toggle-naam-ruimte",
            },
        };
    }

    protected async _onInitialize(): Promise<void> {
        await super._onInitialize();

        this.messages.events.map.initialized.subscribe(async (map) => {
            console.log("Map initialized:", map);
            this.map = map.maps.map;
            this.view = map.maps["view"];

            const ExaggeratedElevationLayer = new BaseElevationLayer

            

    
       
         

        });

        // const config = this.configService.getSettings();
        // this.toggleON = config[this.buttonId] === true;
        // this.messages
        //     .event<UserSettingsChangedEvent>(USERSETTINGS_CHANGED_EVENT)
        //     .subscribe((event) => {
        //         if (event.newValue) {
        //             this.toggleON = event.newValue[this.buttonId] === true;
        //         }
        //     });
    }
}
