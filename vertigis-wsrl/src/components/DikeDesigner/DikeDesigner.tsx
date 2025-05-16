import type am5xy from "@amcharts/amcharts5/xy";
import ArchitectureIcon from "@mui/icons-material/Architecture";
import AssessmentIcon from "@mui/icons-material/Assessment";
import AttachMoneyIcon from "@mui/icons-material/AttachMoney";
import ClearIcon from "@mui/icons-material/Clear";
import CloudDownloadIcon from "@mui/icons-material/CloudDownload";
import EditIcon from "@mui/icons-material/Edit";
import FilterIcon from "@mui/icons-material/Filter";
import MapIcon from "@mui/icons-material/Map";
import PlayCircleFilledWhiteIcon from "@mui/icons-material/PlayCircleFilledWhite";
import SelectAllIcon from "@mui/icons-material/SelectAll";
import TableRowsIcon from "@mui/icons-material/TableRows";
// import TravelExploreIcon from '@mui/icons-material/TravelExplore';
import UploadFileIcon from "@mui/icons-material/UploadFile";
import {
    Box,
    Button,
    ButtonGroup,
    LinearProgress,
    Stack,
    Tab,
    Table,
    TableBody,
    TableCell,
    TableContainer,
    TableRow,
    Tabs,
    TextField,
    Select,
    MenuItem,
    FormControl,
    InputLabel,
} from "@mui/material";
import { LayoutElement } from "@vertigis/web/components";
import type { LayoutElementProperties } from "@vertigis/web/components";
import { useWatchAndRerender } from "@vertigis/web/ui";
import React, { useEffect, useRef, useState } from "react";
import type { ReactElement } from "react";

import type DikeDesignerModel from "./DikeDesignerModel";
import {
    calculateVolume,
    createDesigns,
    exportGraphicsLayerAsGeoJSON,
    initializeChart,
    setInputLineFromFeatureLayer
} from "./Functions/DesignFunctions";
import ChartAndTablePanel from "./SubComponents/ChartAndTablePanel";
// import { SimpleWorker } from "./Workers/SimpleWorker"; // adjust path as needed
const DikeDesigner = (
    props: LayoutElementProperties<DikeDesignerModel>
): ReactElement => {
    const { model } = props;

    // const workerRef = useRef<Worker | null>(null);

    // useEffect(() => {
    //     const blob = new Blob([simpleWorkerCode], { type: "application/javascript" });
    //     const worker = new Worker(URL.createObjectURL(blob));
    //     workerRef.current = worker;

    //     worker.onmessage = (e) => {
    //       console.log("Received from worker:", e.data);
    //     };

    //     // Send test data
    //     worker.postMessage(5);

    //     return () => {
    //       worker.terminate();
    //     };
    //   }, []);

    const chartContainerRef = useRef<HTMLDivElement | null>(null);
    useWatchAndRerender(model, "chartData");

    const [mapLeftBorder, setMapLeftBorder] = useState(0);
    const [mapRightBorder, setMapRightBorder] = useState(window.innerWidth);
    const [activeTab, setActiveTab] = useState(0);
    const [isOverviewVisible, setIsOverviewVisible] = useState(false);
    const [loading, setLoading] = useState(false); // State to track loading status
    const [value, setValue] = React.useState(0);
    const [isLayerListVisible, setIsLayerListVisible] = useState(false);


    const handleChange = (event: React.SyntheticEvent, newValue: number) => {
        setValue(newValue);
    };

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
        initializeChart(model, activeTab, chartContainerRef);

        return () => {
            if (model.chartRoot) {
                model.chartRoot.dispose();
                console.log("Chart disposed");
            }
        }
    }, [model.overviewVisible, model, activeTab, chartContainerRef, model.chartData]);

    const handleDrawLine = () => {
        model.startDrawingLine();
    };

    const handleUploadGeoJSON = () => {
        document.getElementById("geojson-upload")?.click();
    };

    const handleSelectFromMap = () => {
        if (model.lineFeatureLayers?.length > 0) {
            setIsLayerListVisible(true);
        } else {
            console.warn("No line feature layers available.");
        }
    };


    const handleFileChange = (event: React.ChangeEvent<HTMLInputElement>) => {
        const file = event.target.files?.[0];
        if (file) {
            model.handleGeoJSONUpload(file);
        }
    };

    const handleClearGraphics = () => {
        model.graphicsLayerLine.removeAll();
        model.selectedLineLayerId = null;
        model.selectedDijkvakField = null;
    };

    const handleGridChange = (event: React.ChangeEvent<HTMLInputElement>) => {
        model.gridSize = parseFloat(event.target.value);
    }

    const setSelectedLineLayerId = (lineLayerId: string) => {
        model.selectedLineLayerId = lineLayerId;
        model.graphicsLayerLine.removeAll();
        setInputLineFromFeatureLayer(model)

        // Find the selected feature layer
        const selectedLayer = model.lineFeatureLayers.find((layer) => layer.id === lineLayerId);
        if (selectedLayer) {
            // Extract field names from the selected layer
            const fields = selectedLayer.fields.map((field: { name: string }) => field.name);
            model.selectedDijkvakLayerFields = fields;
        }
    };

    // const handleTabChange = (event: React.SyntheticEvent, newValue: number) => {
    //     setActiveTab(newValue);
    // };

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
        model.allChartData[model.activeSheet] = updatedData; // Update the active sheet data

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

        setLoading(true); // Show loader
        try {
            await createDesigns(model);
            await calculateVolume(model);
            console.log("All done...");
        } catch (error) {
            console.error("Error during design creation or volume calculation:", error);
        } finally {
            setLoading(false); // Hide loader
        }
    };

    // const handle2DAnalysis = async () => {
    //     setLoading(true); // Show loader
    //     try {
    //         await convertTo2D(model);
    //         console.log("2D analysis done...");
    //     } catch (error) {
    //         console.error("Error during 2D analysis:", error);
    //     } finally {
    //         setLoading(false); // Hide loader
    //     }
    // };
    const handleClearDesign = () => {
        model.meshes = []
        model.offsetGeometries = []
        model.graphicsLayerTemp.removeAll();
        model.graphicsLayerMesh.removeAll();
        model.totalVolumeDifference = null;
        model.excavationVolume = null;
        model.fillVolume = null;
    };

    const handleExportGraphics = () => {
        exportGraphicsLayerAsGeoJSON(model)
    };

    useWatchAndRerender(model, "excavationVolume");
    useWatchAndRerender(model, "fillVolume)");
    useWatchAndRerender(model, "totalVolumeDifference");
    useWatchAndRerender(model, "graphicsLayerLine.graphics.length");
    useWatchAndRerender(model, "graphicsLayerTemp.graphics.length");
    useWatchAndRerender(model, "chartData.length");
    useWatchAndRerender(model, "overviewVisible");
    useWatchAndRerender(model, "selectedLineLayerId");
    useWatchAndRerender(model, "gridSize");
    useWatchAndRerender(model, "activeSheet");
    useWatchAndRerender(model, "selectedDijkvakField");


    interface TabPanelProps {
        children?: React.ReactNode;
        index: number;
        value: number;
    }

    function a11yProps(index: number) {
        return {
            id: `simple-tab-${index}`,
            'aria-controls': `simple-tabpanel-${index}`,
        };
    }

    function CustomTabPanel(props: TabPanelProps) {
        const { children, value, index, ...other } = props;

        return (
            <div
                role="tabpanel"
                hidden={value !== index}
                id={`simple-tabpanel-${index}`}
                aria-labelledby={`simple-tab-${index}`}
                {...other}
            >
                {value === index && <Box sx={{ p: 3 }}>{children}</Box>}
            </div>
        );
    }


    return (
        <LayoutElement {...props} style={{ width: "100%", overflowY:"scroll" }}>
            <Box
                sx={{ width: '100%' }}
            >
                <Box sx={{ borderBottom: 1, borderColor: 'divider' }}>
                    <Tabs
                        value={value}
                        onChange={handleChange}
                        variant="scrollable"
                        scrollButtons="auto"

                        aria-label="scrollable auto tabs example"

                    >
                        <Tab icon={<ArchitectureIcon />} label="Dimensioneren" {...a11yProps(0)}>
                        </Tab>
                        <Tab icon={<AssessmentIcon />} label="Effecten" {...a11yProps(1)} />
                        <Tab icon={<AttachMoneyIcon />} label="Kosten" {...a11yProps(2)} />
                        <Tab icon={<SelectAllIcon />} label="Selecteren" {...a11yProps(3)} />
                    </Tabs>
                </Box>
                <CustomTabPanel value={value} index={0}>
                    <Stack spacing={1}>

                        <Stack spacing={2} sx={{ outline: 1, padding: 1, borderRadius: 1, outlineColor: "#D3D3D3" }}>
                            <ButtonGroup fullWidth>
                                <Button
                                    disabled={!model.sketchViewModel}
                                    color="primary"
                                    onClick={handleDrawLine}
                                    startIcon={<EditIcon />}
                                    variant="contained"
                                    sx={{
                                        flexDirection: "column", // Stack icon and text vertically
                                        padding: "8px 4px", // Adjust padding for better spacing
                                        fontSize: "9px", // Adjust font size for smaller screens
                                    }}
                                >
                                    Teken lijn
                                </Button>
                                <Button
                                    color="primary"
                                    onClick={handleUploadGeoJSON}
                                    startIcon={<UploadFileIcon />}
                                    variant="contained"
                                    disabled={!model.map}
                                    sx={{
                                        flexDirection: "column", // Stack icon and text vertically
                                        padding: "8px 4px", // Adjust padding for better spacing
                                        fontSize: "9px", // Adjust font size for smaller screens
                                    }}
                                >
                                    Upload GeoJSON
                                </Button>
                                <Button
                                    color="primary"
                                    onClick={handleSelectFromMap}
                                    startIcon={<MapIcon />}
                                    variant="contained"
                                    disabled={!model.map}
                                    sx={{
                                        flexDirection: "column", // Stack icon and text vertically
                                        padding: "8px 4px", // Adjust padding for better spacing
                                        fontSize: "9px", // Adjust font size for smaller screens
                                    }}
                                >
                                    Kies uit kaart
                                </Button>
                            </ButtonGroup>
                            {isLayerListVisible && (
                                <>
                                    {/* Ontwerplijn Dropdown */}
                                    <FormControl sx={{ marginTop: 2, fontSize: "11px" }} size="small">
                                        <InputLabel
                                            id="line-layer-label"
                                            sx={{ fontSize: "11px" }} // Larger font for the label
                                        >
                                            Ontwerplijn
                                        </InputLabel>
                                        <Select
                                            value={model.selectedLineLayerId}
                                            onChange={(e) => setSelectedLineLayerId(e.target.value)}
                                            displayEmpty
                                            fullWidth
                                            variant="outlined"
                                            sx={{
                                                fontSize: "11px", // Larger font for the dropdown text
                                            }}
                                        >
                                            {model.lineFeatureLayers.map((layer) => (
                                                <MenuItem
                                                    key={layer.id}
                                                    value={layer.id}
                                                    sx={{ fontSize: "11px" }} // Larger font for the menu items
                                                >
                                                    {layer.title}
                                                </MenuItem>
                                            ))}
                                        </Select>
                                    </FormControl>

                                    {/* Dijkvak-id Dropdown */}
                                    {model.selectedDijkvakLayerFields.length > 0 && (
                                        <FormControl sx={{ marginTop: 2, fontSize: "14px" }} size="small">
                                            <InputLabel
                                                id="dijkvak-field-label"
                                                sx={{ fontSize: "11px" }} // Larger font for the label
                                            >
                                                Dijkvak-id veld
                                            </InputLabel>
                                            <Select
                                                value={model.selectedDijkvakField || ""}
                                                onChange={(e) => {
                                                    model.selectedDijkvakField = e.target.value; // Store in the model
                                                }}
                                                displayEmpty
                                                fullWidth
                                                variant="outlined"
                                                sx={{
                                                    fontSize: "11px", // Larger font for the dropdown text
                                                }}
                                            >
                                                {model.selectedDijkvakLayerFields.map((field) => (
                                                    <MenuItem
                                                        key={field}
                                                        value={field}
                                                        sx={{ fontSize: "11px" }} // Larger font for the menu items
                                                    >
                                                        {field}
                                                    </MenuItem>
                                                ))}
                                            </Select>
                                        </FormControl>
                                    )}
                                </>
                            )}
                            <Button
                                disabled={!model.graphicsLayerLine?.graphics.length}
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
                                disabled={!model.chartData?.length}
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
                                value={model.gridSize}
                                label="Gridgrootte [m]"
                                type="number"
                                variant="outlined"
                                size="medium"
                                onChange={handleGridChange}
                                sx={{ marginTop: 4 }}
                                InputProps={{
                                    sx: { fontSize: '12px', lineHeight: '2' },
                                }}
                                InputLabelProps={{
                                    sx: { fontSize: '12px' }
                                }}
                            />


                            <Button
                                disabled={!model.chartData?.length || !model.graphicsLayerLine?.graphics.length}
                                variant="contained"
                                color="primary"
                                startIcon={<PlayCircleFilledWhiteIcon />}
                                onClick={handleCreateDesign}
                                fullWidth
                            >
                                Uitrollen in 3D
                            </Button>
                            
                            <Button
                                disabled={!model.chartData?.length || !model.graphicsLayerLine?.graphics.length || !model.selectedDijkvakField}
                                variant="contained"
                                color="primary"
                                startIcon={<PlayCircleFilledWhiteIcon />}
                                onClick={handleCreateDesign}
                                fullWidth
                            >
                                Uitrollen over dijkvakken
                            </Button>
                            {/* <Button
                                disabled={!model.chartData?.length || !model.graphicsLayerLine?.graphics.length || !model.selectedDijkvakField}
                                variant="contained"
                                color="primary"
                                startIcon={<TravelExploreIcon />}
                                onClick={handle2DAnalysis}
                                fullWidth
                            >
                                Ruimtebeslag analyse (2D)
                            </Button> */}
                            <Button
                                disabled={!model.graphicsLayerTemp?.graphics.length}
                                variant="contained"
                                color="secondary"
                                startIcon={<CloudDownloadIcon />}
                                onClick={handleExportGraphics}
                                fullWidth
                            >
                                Download ontwerpdata (GeoJSON)
                            </Button>

                            <Button
                                disabled={!model.graphicsLayerTemp?.graphics.length}
                                variant="outlined"
                                color="primary"
                                startIcon={<ClearIcon />}
                                onClick={handleClearDesign}
                                fullWidth
                            >
                                Verwijder uitrol
                            </Button>

                            {/* Volume table with loader */}
                            <div style={{ position: "relative" }}>
                                {loading && (
                                    <LinearProgress
                                        sx={{
                                            position: "absolute",
                                            top: 0,
                                            left: 0,
                                            width: "100%",
                                            zIndex: 1,
                                        }}
                                    />
                                )}
                                <TableContainer sx={{ marginTop: 2, opacity: loading ? 0.5 : 1 }}>
                                    <Table>
                                        <TableBody>
                                            <TableRow>
                                                <TableCell sx={{ fontSize: 11 }} align="left">
                                                    Totaal volume verschil [m³]
                                                </TableCell>
                                                <TableCell sx={{ fontSize: 11 }} align="right">
                                                    {model.totalVolumeDifference ?? "-"}
                                                </TableCell>
                                            </TableRow>
                                            <TableRow>
                                                <TableCell sx={{ fontSize: 11 }} align="left">
                                                    Uitgravingsvolume [m³]
                                                </TableCell>
                                                <TableCell sx={{ fontSize: 11 }} align="right">
                                                    {model.excavationVolume ?? "-"}
                                                </TableCell>
                                            </TableRow>
                                            <TableRow>
                                                <TableCell sx={{ fontSize: 11 }} align="left">
                                                    Opvulvolume [m³]
                                                </TableCell>
                                                <TableCell sx={{ fontSize: 11 }} align="right">
                                                    {model.fillVolume ?? "-"}
                                                </TableCell>
                                            </TableRow>
                                        </TableBody>
                                    </Table>
                                </TableContainer>
                            </div>
                        </Stack>
                    </Stack>
                </CustomTabPanel>
            </Box>


            {/* Paper for Chart and Table */}
            {isOverviewVisible && model.chartData && (
                <ChartAndTablePanel
                    isOverviewVisible={isOverviewVisible}
                    setIsOverviewVisible={setIsOverviewVisible}
                    activeTab={activeTab}
                    setActiveTab={setActiveTab}
                    mapLeftBorder={mapLeftBorder}
                    mapRightBorder={mapRightBorder}
                    chartContainerRef={chartContainerRef}
                    model={model}
                    handleCellChange={handleCellChange}
                />
            )}

        </LayoutElement>
    );
};

export default DikeDesigner;
