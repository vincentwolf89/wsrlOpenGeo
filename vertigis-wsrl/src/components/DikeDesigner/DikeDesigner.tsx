/* eslint-disable prefer-const */
/* eslint-disable @typescript-eslint/no-floating-promises */
/* eslint-disable @typescript-eslint/no-unsafe-argument */
/* eslint-disable @typescript-eslint/no-unused-vars */
/* eslint-disable @typescript-eslint/consistent-type-imports */
/* eslint-disable import/order */

import React, { useState, useEffect, useRef } from "react"; // <== Added useRef
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
    Paper,
    IconButton,
    Tabs,
    Tab,
    Table,
    TableBody,
    TableCell,
    TableContainer,
    TableHead,
    TableRow,
    TextField,
} from "@mui/material";
import { LayoutElement } from "@vertigis/web/components";
import type { LayoutElementProperties } from "@vertigis/web/components";
import { useWatchAndRerender } from "@vertigis/web/ui";
import * as XLSX from "xlsx";
import * as am5 from "@amcharts/amcharts5";
import * as am5xy from "@amcharts/amcharts5/xy";
import am5themes_Animated from "@amcharts/amcharts5/themes/Animated";

import type DikeDesignerModel from "./DikeDesignerModel";

const DikeDesigner = (
    props: LayoutElementProperties<DikeDesignerModel>
): ReactElement => {
    const { model } = props;

    useWatchAndRerender(model, "chartData");

    const [mapLeftBorder, setMapLeftBorder] = useState(0);
    const [mapRightBorder, setMapRightBorder] = useState(window.innerWidth);
    const [activeTab, setActiveTab] = useState(0);

    // NEW: Add Refs to store chart root + series
    const chartRootRef = useRef<am5.Root | null>(null);
    const seriesRef = useRef<am5xy.LineSeries | null>(null);

    const observeMapLeftBorder = () => {
        const mapElement = document.querySelector(".gcx-map");
        if (mapElement) {
            const observer = new ResizeObserver((entries) => {
                for (const item of entries) {
                    if (item.contentRect) {
                        const positionLeft = mapElement.getBoundingClientRect().left;
                        const positionRight = mapElement.getBoundingClientRect().right;
                        setMapLeftBorder(positionLeft);
                        setMapRightBorder(positionRight);
                    }
                }
            });
            observer.observe(mapElement);
            return () => observer.disconnect();
        }
    };

    useEffect(() => {
        const disconnectObserver = observeMapLeftBorder();
        return () => {
            if (disconnectObserver) disconnectObserver();
        };
    }, []);

    const handleClearExcel = () => {
        model.chartData = null;
    };

    const closeOverview = () => {
        model.chartData = null;
    };

    useEffect(() => {
        if (activeTab === 0 && model.chartData) {
            const root = am5.Root.new("chartdiv");
    
            root.setThemes([am5themes_Animated.new(root)]);
    
            const chart = root.container.children.push(
                am5xy.XYChart.new(root, {
                    panX: true,
                    panY: true,
                    wheelX: "panX",
                    wheelY: "zoomX",
                    pinchZoomX: true,
                })
            );
    
            const xAxis = chart.xAxes.push(
                am5xy.ValueAxis.new(root, {
                    renderer: am5xy.AxisRendererX.new(root, {}),
                    tooltip: am5.Tooltip.new(root, {}),
                })
            );
    
            const yAxis = chart.yAxes.push(
                am5xy.ValueAxis.new(root, {
                    renderer: am5xy.AxisRendererY.new(root, {}),
                    tooltip: am5.Tooltip.new(root, {}),
                })
            );
    
            const series = chart.series.push(
                am5xy.LineSeries.new(root, {
                    name: "Hoogte vs Afstand",
                    xAxis: xAxis as any,
                    yAxis: yAxis as any,
                    valueYField: "hoogte",
                    valueXField: "afstand",
                    tooltip: am5.Tooltip.new(root, {
                        labelText: "{valueY}",
                    }),
                })
            );
    
            series.data.setAll(model.chartData);
    
            series.strokes.template.setAll({
                strokeWidth: 2,
            });
    
            // Add draggable bullets with snapping logic
            series.bullets.push((root, series, dataItem) => {
                const circle = am5.Circle.new(root, {
                    radius: 5,
                    fill: root.interfaceColors.get("background"),
                    stroke: series.get("fill"),
                    strokeWidth: 2,
                    draggable: true,
                    interactive: true,
                    cursorOverStyle: "pointer",
                });
    
                // Snap the coordinates to the nearest 0.5 meter
                const snapToGrid = (value: number, gridSize: number) => Math.round(value / gridSize) * gridSize;
    
                circle.events.on("dragstop", () => {
                    // Calculate new positions
                    const newY = yAxis.positionToValue(
                        yAxis.coordinateToPosition(circle.y())
                    );
                    const newX = xAxis.positionToValue(
                        xAxis.coordinateToPosition(circle.x())
                    );
    
                    // Snap to nearest 0.5 meter grid
                    const snappedX = snapToGrid(newX, 0.5);
                    const snappedY = snapToGrid(newY, 0.5);
    
                    // Update chart
                    dataItem.set("valueY", snappedY);
                    dataItem.set("valueX", snappedX);
    
                    // Update model.chartData
                    const index = model.chartData.findIndex(
                        (d) => d.afstand === dataItem.dataContext["afstand"]
                    );
    
                    if (index !== -1) {
                        model.chartData[index].hoogte = snappedY;
                        model.chartData[index].afstand = snappedX;
                        model.chartData = [...model.chartData]; // Force reactivity
                    }
                });
    
                return am5.Bullet.new(root, {
                    sprite: circle,
                });
            });
    
            chart.set("cursor", am5xy.XYCursor.new(root, {}));
    
            return () => {
                root.dispose();
            };
        }
    }, [activeTab, model.chartData, model]);
    

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
            model.handleGeoJSONUpload(file);
        }
    };

    const handleClearGraphics = () => {
        model.graphicsLayerLine.removeAll();
    };

    const handleTabChange = (event: React.SyntheticEvent, newValue: number) => {
        setActiveTab(newValue);
    };

    const handleCellChange = (rowIndex: number, colKey: string, value: string) => {
        const updatedData = [...model.chartData];
        const parsedValue = ["afstand", "hoogte"].includes(colKey)
            ? parseFloat(value)
            : value;

        updatedData[rowIndex] = {
            ...updatedData[rowIndex],
            [colKey]: parsedValue,
        };

        model.chartData = updatedData;

        // 🔁 Update chart with new data
        seriesRef.current?.data.setAll(updatedData);
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
                                    onChange={model.handleExcelUpload}
                                />
                            </Button>
                            <Button
                                variant="outlined"
                                color="secondary"
                                startIcon={<ClearIcon />}
                                onClick={handleClearExcel}
                                fullWidth
                            >
                                Verwijder Excel
                            </Button>
                        </Stack>
                    </AccordionDetails>
                </Accordion>

                {/* Paper for Chart and Table */}
                {model.chartData && (
                    <Paper
                        elevation={3}
                        sx={{
                            position: "fixed",
                            bottom: 0,
                            left: mapLeftBorder, // Dynamically set left position
                            width: mapRightBorder - mapLeftBorder, // Dynamically set width
                            height: "50%", // Consume half of the map's height
                            zIndex: 10,
                            padding: 0,
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
                            Design overzicht
                            <IconButton
                                aria-label="close"
                                onClick={closeOverview} // Close the Paper when clearing Excel data
                                size="medium"
                                sx={{ color: "#ffffff" }}
                            >
                                <CloseIcon />
                            </IconButton>
                        </Typography>
                        <Tabs
                            value={activeTab}
                            onChange={handleTabChange}
                            indicatorColor="primary"
                            textColor="primary"
                            variant="fullWidth"
                        >
                            <Tab label="Dwarsprofiel" />
                            <Tab label="Invoerdata" />
                        </Tabs>
                        {activeTab === 0 && (
                            <div
                                id="chartdiv"
                                style={{
                                    width: "100%",
                                    height: "calc(100% - 40px)", // Adjust height to fit within the Paper
                                }}
                            ></div>
                        )}
                        {activeTab === 1 && (
                            <TableContainer
                                sx={{
                                    height: "calc(100% - 40px)", // Adjust height to fit within the Paper
                                    overflow: "auto",
                                }}
                            >
                                <Table stickyHeader>
                                    <TableHead>
                                        <TableRow>
                                            {/* Render table headers based on the keys of the first object in sortedData */}
                                            {model.chartData?.length > 0 &&
                                                Object.keys(model.chartData[0]).map((header) => (
                                                    <TableCell key={header} align="center">
                                                        {header.charAt(0).toUpperCase() + header.slice(1)}
                                                    </TableCell>
                                                ))}
                                        </TableRow>
                                    </TableHead>
                                    <TableBody>
                                        {model.chartData?.map((row, rowIndex) => {
                                            const rowKey = `afstand-${row.afstand ?? rowIndex}`; // Fallback to index if needed
                                            return (
                                                <TableRow key={rowKey}>
                                                    {Object.entries(row).map(([key, cell]) => (
                                                        <TableCell key={`${rowKey}-${key}`} align="center">
                                                            <TextField
                                                                value={cell}
                                                                onChange={(e) => handleCellChange(rowIndex, key, e.target.value)} // Pass `key` instead of `colIndex`
                                                                variant="outlined"
                                                                size="small"
                                                            />
                                                        </TableCell>
                                                    ))}
                                                </TableRow>
                                            );
                                        })}
                                    </TableBody>
                                </Table>
                            </TableContainer>
                        )}
                    </Paper>
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
