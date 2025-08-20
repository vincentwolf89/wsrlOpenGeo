/* eslint-disable @typescript-eslint/no-floating-promises */
import { LayoutElement } from "@vertigis/web/components";
import type { LayoutElementProperties } from "@vertigis/web/components";
import { useWatchAndRerender } from "@vertigis/web/ui";
import Box from "@vertigis/web/ui/Box";
import Slider from '@vertigis/web/ui/Slider/Slider';
import type { ReactElement } from "react";

import type ElevationExaggeratorModel from "./ElevationExaggeratorModel";

const ElevationExaggerator = (
    props: LayoutElementProperties<ElevationExaggeratorModel>
): ReactElement => {
    const { model } = props;

    useWatchAndRerender(model, "exaggeration");

    return (
        <LayoutElement {...props}>
            <Box sx={{ width: 300, height: 100, p: "32px", display: 'flex', flexDirection: 'column', alignItems: 'center' }}>
                <Box sx={{ alignSelf: 'flex-start', mb: 1, fontWeight: 600 }}>
                    Hoogte factor:
                </Box>
                <Slider
                    value={model.exaggeration}
                    onChange={(event, value) => {
                        model.exaggeration = value as number;
                        model.processChange();
                    }}
                    aria-label="Elevation Exaggeration"
                    defaultValue={1}
                    valueLabelDisplay="auto"
                    step={0.2}
                    marks
                    min={1}
                    max={2}
                />
            </Box>
        </LayoutElement>
    );
};

export default ElevationExaggerator;
