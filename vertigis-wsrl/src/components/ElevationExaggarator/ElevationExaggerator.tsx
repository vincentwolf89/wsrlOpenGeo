/* eslint-disable @typescript-eslint/no-floating-promises */
import CheckBoxIcon from "@mui/icons-material/CheckBox";
import CheckBoxOutlineBlankIcon from "@mui/icons-material/CheckBoxOutlineBlank";
import LabelIcon from "@mui/icons-material/Label";
import  Box  from "@vertigis/web/ui/Box";
import { LayoutElement } from "@vertigis/web/components";
import type { LayoutElementProperties } from "@vertigis/web/components";
import { useWatchAndRerender } from "@vertigis/web/ui";
import Slider from '@vertigis/web/ui/Slider/Slider';
import type { ReactElement } from "react";

import type ElevationExaggeratorModel from "./ElevationExaggeratorModel";

const ElevationExaggerator = (
    props: LayoutElementProperties<ElevationExaggeratorModel>
): ReactElement => {
    const { model } = props;

    useWatchAndRerender(model, "toggleON");
    useWatchAndRerender(model, "buttonName");

    return (
        <LayoutElement {...props}>
    <Box sx={{ width: 300 }}>
   <Slider
  aria-label="Temperature"
  defaultValue={30}
  valueLabelDisplay="auto"
  shiftStep={30}
  step={10}
  marks
  min={10}
  max={110}
/>
    </Box>
        </LayoutElement>
    );
};

export default ElevationExaggerator;
