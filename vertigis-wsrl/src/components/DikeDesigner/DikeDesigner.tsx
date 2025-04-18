/* eslint-disable prefer-const */
/* eslint-disable @typescript-eslint/no-floating-promises */
/* eslint-disable @typescript-eslint/no-unsafe-argument */
/* eslint-disable @typescript-eslint/no-unused-vars */
/* eslint-disable @typescript-eslint/consistent-type-imports */
/* eslint-disable import/order */

import React, { useState } from "react";
import type { ReactElement } from "react";
import ExpandMoreIcon from "@mui/icons-material/ExpandMore";
import EditIcon from "@mui/icons-material/Edit";
import UploadFileIcon from "@mui/icons-material/UploadFile";
import MapIcon from "@mui/icons-material/Map";
import CloseIcon from "@mui/icons-material/Close";
import ClearIcon from "@mui/icons-material/Clear";
import Draggable from "react-draggable";
import {
    Button,
    ButtonGroup,
    Stack,
    Accordion,
    AccordionSummary,
    AccordionDetails,
    Typography,
    Table,
    TableBody,
    TableCell,
    TableContainer,
    TableHead,
    TableRow,
    Paper,
    Dialog,
    DialogTitle,
    DialogContent,
    IconButton,
} from "@mui/material";
import { LayoutElement } from "@vertigis/web/components";
import type { LayoutElementProperties } from "@vertigis/web/components";
import { useWatchAndRerender } from "@vertigis/web/ui";
import * as XLSX from "xlsx";
import { Line } from "react-chartjs-2";
import {
    Chart as ChartJS,
    CategoryScale,
    LinearScale,
    PointElement,
    LineElement,
    Title,
    Tooltip,
    Legend,
} from "chart.js";

import type DikeDesignerModel from "./DikeDesignerModel";

// Register Chart.js components
ChartJS.register(CategoryScale, LinearScale, PointElement, LineElement, Title, Tooltip, Legend);

const DikeDesigner = (
    props: LayoutElementProperties<DikeDesignerModel>
): ReactElement => {
    const { model } = props;

    const [excelData, setExcelData] = useState<any[]>([]);
    const [chartData, setChartData] = useState<any>(null);
    const [isDialogOpen, setIsDialogOpen] = useState(false);
    const [previousChartData, setPreviousChartData] = useState<any>(null);

    const handleExcelUpload = (event: React.ChangeEvent<HTMLInputElement>) => {
        const fileInput = event.target; // Reference to the file input
        const file = fileInput.files?.[0];
        if (file) {
            const reader = new FileReader();
            reader.onload = (e) => {
                const data = new Uint8Array(e.target?.result as ArrayBuffer);
                const workbook = XLSX.read(data, { type: "array" });
                const sheetName = workbook.SheetNames[0];
                const sheet = workbook.Sheets[sheetName];
                const jsonData = XLSX.utils.sheet_to_json(sheet, { header: 1 });

                // Set Excel data for the table
                setExcelData(jsonData);

                // Prepare chart data
                if (jsonData.length > 1) {
                    const labels = jsonData.slice(1).map((row: any[]) => row[0]); // "naam" column for labels
                    const afstand = jsonData.slice(1).map((row: any[]) => row[1]); // "afstand" column for X-axis
                    const hoogte = jsonData.slice(1).map((row: any[]) => row[2]); // "hoogte" column for Y-axis

                    const newChartData = {
                        labels: afstand, // Use "afstand" for the X-axis
                        datasets: [
                            {
                                label: "Hoogte vs Afstand",
                                data: hoogte, // Use "hoogte" for the Y-axis
                                borderColor: "rgba(75, 192, 192, 1)",
                                backgroundColor: "rgba(75, 192, 192, 0.2)",
                                tension: 0.0, // Straight lines
                            },
                        ],
                    };

                    setChartData(newChartData); // Update chartData to trigger UI update
                    setPreviousChartData(newChartData); // Update previousChartData for reopening
                }
            };
            reader.readAsArrayBuffer(file);
        }

        // Reset the file input value to allow reuploading the same file
        fileInput.value = "";
    };

    const handleClearExcel = () => {
        setExcelData([]);
        setChartData(null); // Clear chartData to hide the Paper
        setPreviousChartData(null); // Clear previousChartData to avoid reopening stale data
    };

    const handleCloseDialog = () => {
        setIsDialogOpen(false);
    };

    const handleDrawLine = () => {
        model.startDrawingLine();
    };

    const handleUploadGeoJSON = () => {
        document.getElementById("geojson-upload")?.click();
    };

    const handleSelectFromMap = () => {
        model.selectLineFromMap();
    };

    const handleFileChange = (event: React.ChangeEvent<HTMLInputElement>) => {
        const file = event.target.files?.[0];
        if (file) {
            model.handleGeoJSONUpload(file); // Call the model's method
        }
    };

    const handleClearGraphics = () => {
        model.graphicsLayerLine.removeAll(); // Call the model's method to clear the graphics layer
    };


    useWatchAndRerender(model, "selectedTheme");
    useWatchAndRerender(model, "msRouteOn");
    useWatchAndRerender(model, "ovGroepOn");

    return (
        <LayoutElement {...props}>
            <Stack
                direction="column"
                spacing={2}
                justifyContent="flex-start"
                alignContent="stretch"
                sx={{ width: "100%" }}
            >
                <Accordion sx={{ width: "100%" }} defaultExpanded>
                    <AccordionSummary expandIcon={<ExpandMoreIcon />}>
                        <Typography
                            sx={{
                                fontSize: 14,
                                fontWeight: "",
                                fontFamily: "var(--defaultFont)",
                            }}
                        >
                            Dimensioneren
                        </Typography>
                    </AccordionSummary>
                    <AccordionDetails>
                        <Stack spacing={2}>
                            <ButtonGroup fullWidth>
                                <Button
                                    color="primary"
                                    onClick={handleDrawLine}
                                    startIcon={<EditIcon />}
                                >
                                    Teken lijn
                                </Button>
                                <Button
                                    color="primary"
                                    onClick={handleUploadGeoJSON}
                                    startIcon={<UploadFileIcon />}
                                >
                                    Upload GeoJSON
                                </Button>
                                <Button
                                    color="primary"
                                    onClick={handleSelectFromMap}
                                    startIcon={<MapIcon />}
                                    disabled
                                >
                                    Selecteer uit de kaart
                                </Button>
                            </ButtonGroup>
                            <Button
                                variant="contained"
                                color="primary"
                                onClick={handleClearGraphics}
                                fullWidth
                            >
                                Verwijder lijn
                            </Button>
                            {/* Hidden input for GeoJSON upload */}
                            <input
                                id="geojson-upload"
                                type="file"
                                accept=".geojson"
                                hidden
                                onChange={handleFileChange}
                            />
                             <Button
                                variant="contained"
                                component="label"
                                color="primary"
                                fullWidth
                            >
                                Upload Excel
                                <input
                                    type="file"
                                    accept=".xlsx, .xls"
                                    hidden
                                    onChange={handleExcelUpload}
                                />
                            </Button>
                            <Button
                                variant="outlined"
                                color="secondary"
                                startIcon={<ClearIcon />}
                                onClick={handleClearExcel}
                                fullWidth
                            >
                                Clear Excel Data
                            </Button>
                        </Stack>
                    </AccordionDetails>
                </Accordion>

                {/* Paper for Chart */}
                {chartData && (
                    <Paper
                        elevation={3}
                        sx={{
                            position: "fixed",
                            bottom: 0,
                            right: 0,
                            zIndex: 10,
                            padding: 0,
                            width: "600px",
                            height: "50%", // Consume half of the map's height
                            borderRadius: "5px",
                            backgroundColor: "#ffffff",
                            boxShadow: "0px 6px 15px rgba(0, 0, 0, 0.15)",
                        }}
                    >
                        <Typography
                            variant="h6"
                            sx={{
                                fontWeight: "bold",
                                color: "#ffffff",
                                backgroundColor: "#1976d2",
                                padding: 1,
                                fontSize: "12px",
                                borderTopLeftRadius: "4px",
                                borderTopRightRadius: "4px",
                                display: "flex",
                                justifyContent: "space-between",
                                alignItems: "center",
                            }}
                        >
                            Design Data Plot
                            <IconButton
                                aria-label="close"
                                onClick={handleClearExcel} // Close the Paper when clearing Excel data
                                size="medium"
                                sx={{ color: "#ffffff" }}
                            >
                                <CloseIcon />
                            </IconButton>
                        </Typography>
                        <div
                            style={{
                                height: "calc(100% - 40px)", // Adjust height to fit within the Paper
                                overflow: "hidden",
                            }}
                        >
                            <Line
                                data={chartData}
                                options={{
                                    responsive: true,
                                    maintainAspectRatio: false,
                                    plugins: {
                                        legend: {
                                            position: "top",
                                        },
                                        title: {
                                            display: true,
                                            text: "Hoogte vs Afstand",
                                        },
                                    },
                                    scales: {
                                        x: {
                                            title: {
                                                display: true,
                                                text: "Afstand",
                                            },
                                        },
                                        y: {
                                            title: {
                                                display: true,
                                                text: "Hoogte",
                                            },
                                        },
                                    },
                                }}
                            />
                        </div>
                    </Paper>
                )}

                {/* Open Button for Paper */}
                {!chartData && (
                    <Button
                        variant="contained"
                        color="primary"
                        onClick={() => setChartData(previousChartData)} // Restore the chart data to reopen the Paper
                        sx={{
                            position: "fixed",
                            bottom: 25,
                            right: 25,
                            zIndex: 10,
                        }}
                    >
                        Open Chart
                    </Button>
                )}

                <Accordion sx={{ width: "100%" }}>
                    <AccordionSummary expandIcon={<ExpandMoreIcon />}>
                        <Typography
                            sx={{
                                fontSize: 14,
                                fontWeight: "",
                                fontFamily: "var(--defaultFont)",
                            }}
                        >
                            Effecten
                        </Typography>
                    </AccordionSummary>
                    <AccordionDetails>
                        <Typography sx={{ fontFamily: "var(--defaultFont)", fontSize: 12 }}>
                            Content for Effecten goes here.
                        </Typography>
                    </AccordionDetails>
                </Accordion>

                <Accordion sx={{ width: "100%" }}>
                    <AccordionSummary expandIcon={<ExpandMoreIcon />}>
                        <Typography
                            sx={{
                                fontSize: 14,
                                fontWeight: "",
                                fontFamily: "var(--defaultFont)",
                            }}
                        >
                            Kosten
                        </Typography>
                    </AccordionSummary>
                    <AccordionDetails>
                        <Typography sx={{ fontFamily: "var(--defaultFont)", fontSize: 12 }}>
                            Content for Kosten goes here.
                        </Typography>
                    </AccordionDetails>
                </Accordion>

                <Accordion sx={{ width: "100%" }}>
                    <AccordionSummary expandIcon={<ExpandMoreIcon />}>
                        <Typography
                            sx={{
                                fontSize: 14,
                                fontWeight: "",
                                fontFamily: "var(--defaultFont)",
                            }}
                        >
                            Selecteren
                        </Typography>
                    </AccordionSummary>
                    <AccordionDetails>
                        <Typography sx={{ fontFamily: "var(--defaultFont)", fontSize: 12 }}>
                            Content for Selecteren goes here.
                        </Typography>
                    </AccordionDetails>
                </Accordion>
            </Stack>
        </LayoutElement>
    );
};

export default DikeDesigner;
