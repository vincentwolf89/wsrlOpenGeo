import AssessmentIcon from "@mui/icons-material/Assessment";
import { Stack, Button } from "@mui/material";
import React from "react";

import { getIntersectingFeatures } from "../Functions/EffectFunctions";

interface EffectAnalysisPanelProps {
    model: any;
    // onEffectAnalysis?: () => void;
}



const EffectAnalysisPanel: React.FC<EffectAnalysisPanelProps> = ({
    model,

}) => {

    const handleTest = () => {
        getIntersectingFeatures(model, "test")
        console.log("Effect analysis triggered");
    };

    return (
    <Stack spacing={1}>
        <Button
            variant="contained"
            color="primary"
            startIcon={<AssessmentIcon />}
            onClick={handleTest}
            fullWidth
        >
            Voer effectenanalyse uit
        </Button>
        {/* Add more content for the Effecten tab here */}
    </Stack>
    );
}



export default EffectAnalysisPanel;