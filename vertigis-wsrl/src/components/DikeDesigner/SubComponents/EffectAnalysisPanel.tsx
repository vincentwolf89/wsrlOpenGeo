import AssessmentIcon from "@mui/icons-material/Assessment";
import { Stack, Button, Table, TableBody, TableCell, TableContainer, TableHead, TableRow, Paper } from "@mui/material";
import { useWatchAndRerender } from "@vertigis/web/ui";
import React from "react";

import type DikeDesignerModel from "../DikeDesignerModel";
import { getIntersectingFeatures } from "../Functions/EffectFunctions";

interface EffectAnalysisPanelProps {
    model: DikeDesignerModel;
}

const EffectAnalysisPanel: React.FC<EffectAnalysisPanelProps> = ({
    model,

}) => {

    const handleTest = async () => {
        model.messages.commands.ui.displayBusyState.execute({}).catch((error) => {
            console.error("Error displaying busy state:", error);
        });
        await getIntersectingFeatures(model, "BAG 2D").then((result) => {
            model.intersectingPanden = result;
            console.log("Intersecting panden:", result);
        }).catch((error) => {
            console.error("Error fetching intersecting features:", error);
        });

        await getIntersectingFeatures(model, "Bomenregister 2015").then((result) => {
            model.intersectingBomen = result;   
            console.log("Intersecting bomen:", result);
        }).catch((error) => {
            console.error("Error fetching intersecting features:", error);
        });

        await getIntersectingFeatures(model, "DKK - perceel").then((result) => {
            model.intersectingPercelen = result;   
            console.log("Intersecting percelen:", result);
        }).catch((error) => {
            console.error("Error fetching intersecting features:", error);
        });

        model.messages.commands.ui.hideBusyState.execute().catch((error) => {
            console.error("Error displaying busy state:", error);
        });

    };

    useWatchAndRerender(model, "intersectingPanden")
    useWatchAndRerender(model, "intersectingBomen")
    useWatchAndRerender(model, "intersectingPercelen")

    return (
        <Stack spacing={2}>
            <Button
                variant="contained"
                color="primary"
                startIcon={<AssessmentIcon />}
                onClick={handleTest}
                fullWidth
            >
                Voer effectenanalyse uit
            </Button>
            {/* Summary Table */}
            <TableContainer component={Paper} sx={{  }}>
                <Table >
                    <TableHead>
                        <TableRow>
                            <TableCell sx={{ fontSize: "11px", fontWeight: "bold"  }}>Thema</TableCell>
                            <TableCell align="right" sx={{ fontSize: "11px",fontWeight: "bold" }}>Aantal geraakte elementen</TableCell>
                        </TableRow>
                    </TableHead>
                    <TableBody>
                        <TableRow>
                            <TableCell sx={{ fontSize: "11px"}}>BAG panden</TableCell>
                            <TableCell  sx={{ fontSize: "11px"}} align="right">{model.intersectingPanden?.length}</TableCell>
                        </TableRow>
                        <TableRow>
                            <TableCell sx={{ fontSize: "11px"}}>Bomen</TableCell>
                            <TableCell  sx={{ fontSize: "11px"}} align="right">{model.intersectingBomen?.length}</TableCell>
                        </TableRow>
                        <TableRow>
                            <TableCell sx={{ fontSize: "11px"}}>Percelen</TableCell>
                            <TableCell  sx={{ fontSize: "11px"}} align="right">{model.intersectingPercelen?.length}</TableCell>
                        </TableRow>
                    </TableBody>
                </Table>
            </TableContainer>
        </Stack>
    );
};

export default EffectAnalysisPanel;