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
import PlayCircleFilledWhiteIcon from '@mui/icons-material/PlayCircleFilledWhite';
import TableRowsIcon from '@mui/icons-material/TableRows';
import FilterIcon from '@mui/icons-material/Filter';
import AssessmentIcon from "@mui/icons-material/Assessment";
import AttachMoneyIcon from "@mui/icons-material/AttachMoney";
import SelectAllIcon from "@mui/icons-material/SelectAll";
import ShowChartIcon from "@mui/icons-material/ShowChart";
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
import { calculateVolume, createDesign } from "./Functions/DesignFunctions";

const DikeDesigner = (
    props: LayoutElementProperties<DikeDesignerModel>
): ReactElement => {
    const { model } = props;

    useWatchAndRerender(model, "chartData");

    const [mapLeftBorder, setMapLeftBorder] = useState(0);
    const [mapRightBorder, setMapRightBorder] = useState(window.innerWidth);
    const [activeTab, setActiveTab] = useState(0);
    const [isOverviewVisible, setIsOverviewVisible] = useState(false);
    const [gridSize, setGridSize] = useState(1); // Default grid size

  
    // const chartRootRef = useRef<am5.Root | null>(null);
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

    const handleGridChange = (event: React.ChangeEvent<HTMLInputElement>) => {
        setGridSize(parseFloat(event.target.value));
        model.gridSize = parseFloat(event.target.value);
    }

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

    const handleOpenOverview = () => {
        setIsOverviewVisible(true);
        const updatedData = [...model.chartData];
        model.chartData = updatedData
        seriesRef.current?.data.setAll(model.chartData);
    };

    const handleClearExcel = () => {
        model.chartData = null;
    };
    const handleExcelUpload = (event: React.ChangeEvent<HTMLInputElement>) => {

        setIsOverviewVisible(true); // Close the overview when uploading a new Excel file
        model.handleExcelUpload(event);
    }
    const handleCreateDesign = async () => {
        await createDesign(model);
        await calculateVolume(model);
    };
    const handleClearDesign = () => {
        model.graphicsLayerTemp.removeAll();
        model.totalVolumeDifference = null;
        model.excavationVolume = null;
        model.fillVolume = null;
    };

    useWatchAndRerender(model, "excavationVolume");
    useWatchAndRerender(model, "fillVolume)");
    useWatchAndRerender(model, "totalVolumeDifference");



    return (
        <LayoutElement {...props}>
            <Stack
                direction="column"
                spacing={0}
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
                                display: "flex",
                                alignItems: "center",
                            }}
                        >
                            <ShowChartIcon sx={{ marginRight: 1 }} /> Dimensioneren
                        </Typography>
                    </AccordionSummary>
                    <AccordionDetails>
                        <Stack spacing={1}>

                            <Stack spacing={1} sx={{ outline: 1, padding: 1, borderRadius: 1, outlineColor: "#D3D3D3" }}>
                                <ButtonGroup fullWidth>
                                    <Button
                                        disabled={!model.sketchViewModel}
                                        color="primary"
                                        onClick={handleDrawLine}
                                        startIcon={<EditIcon />}
                                        variant="contained"
                                    >
                                        Teken lijn
                                    </Button>
                                    <Button
                                        color="primary"
                                        onClick={handleUploadGeoJSON}
                                        startIcon={<UploadFileIcon />}
                                        variant="contained"
                                    >
                                        Upload GeoJSON
                                    </Button>
                                    <Button
                                        color="primary"
                                        onClick={handleSelectFromMap}
                                        startIcon={<MapIcon />}
                                        variant="contained"
                                        disabled
                                    >
                                        Selecteer uit de kaart
                                    </Button>
                                </ButtonGroup>
                                <Button
                                    variant="outlined"
                                    color="primary"
                                    onClick={handleClearGraphics}
                                    startIcon={<ClearIcon />}
                                    fullWidth
                                >
                                    Verwijder lijn
                                </Button>
                            </Stack>

                            <Stack spacing={1} sx={{ outline: 1, padding: 1, borderRadius: 1, outlineColor: "#D3D3D3" }}>
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
                                    startIcon={<TableRowsIcon />}
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
                                    Verwijder Excel
                                </Button>
                            </Stack>
                            <Stack spacing={1.5} sx={{ outline: 1, padding: 1, borderRadius: 1, outlineColor: "#D3D3D3" }}>
                                <Button
                                    variant="contained"
                                    color="primary"
                                    startIcon={<FilterIcon />}
                                    onClick={handleOpenOverview}
                                    fullWidth
                                    disabled={!model.chartData?.length || isOverviewVisible}
                                >
                                    Toon ontwerp-paneel
                                </Button>

    
                                {/* Grid-size input */}
                                <TextField
                                    value={gridSize}
                                    label="Gridgrootte [m]"
                                    type="number"
                                    variant="outlined"
                                    size="medium"
                                    onChange={handleGridChange}
                                    sx={{marginTop: 4}}
                                    InputProps={{
                                        sx: { fontSize: '12px', lineHeight: '2' },
                                    }}
                                    InputLabelProps={{
                                        sx: { fontSize: '12px' }
                                    }}
                                />


                                <Button
                                    variant="contained"
                                    color="primary"
                                    startIcon={<PlayCircleFilledWhiteIcon />}
                                    onClick={handleCreateDesign}
                                    fullWidth
                                >
                                    Uitrollen in 3D
                                </Button>

                                <Button
                                    variant="outlined"
                                    color="primary"
                                    startIcon={<ClearIcon />}
                                    onClick={handleClearDesign}
                                    fullWidth
                                >
                                    Verwijder uitrol
                                </Button>
                                
                                {/* Volume table */}
                                <TableContainer sx={{ marginTop: 2 }}>
                                    <Table>
                                        <TableBody>
                                            <TableRow>
                                                <TableCell sx={{fontSize:11}} align="left">Totaal volume verschil [m³]</TableCell>
                                                <TableCell sx={{fontSize:11}} align="right">{model.totalVolumeDifference ?? "-"}</TableCell>
                                            </TableRow>
                                            <TableRow>
                                                <TableCell sx={{fontSize:11}} align="left">Uitgravingsvolume [m³]</TableCell>
                                                <TableCell sx={{fontSize:11}} align="right">{model.excavationVolume ?? "-"}</TableCell>
                                            </TableRow>
                                            <TableRow>
                                                <TableCell sx={{fontSize:11}} align="left">Opvolume [m³]</TableCell>
                                                <TableCell sx={{fontSize:11}} align="right">{model.fillVolume ?? "-"}</TableCell>
                                            </TableRow>
                                        </TableBody>
                                    </Table>
                                </TableContainer>

                            </Stack>
                        </Stack>
                    </AccordionDetails>
                </Accordion>

                {/* Paper for Chart and Table */}
                {isOverviewVisible && model.chartData && (
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
                                onClick={() => setIsOverviewVisible(false)} // Close the Paper when clearing Excel data
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
                                display: "flex",
                                alignItems: "center",
                            }}
                        >
                            <AssessmentIcon sx={{ marginRight: 1 }} /> Effecten
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
                                display: "flex",
                                alignItems: "center",
                            }}
                        >
                            <AttachMoneyIcon sx={{ marginRight: 1 }} /> Kosten
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
                                display: "flex",
                                alignItems: "center",
                            }}
                        >
                            <SelectAllIcon sx={{ marginRight: 1 }} /> Selecteren
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
