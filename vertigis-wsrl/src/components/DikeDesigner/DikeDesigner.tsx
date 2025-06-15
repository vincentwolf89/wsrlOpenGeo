import type am5xy from "@amcharts/amcharts5/xy";
import ArchitectureIcon from "@mui/icons-material/Architecture";
import AssessmentIcon from "@mui/icons-material/Assessment";
import AttachMoneyIcon from "@mui/icons-material/AttachMoney";
import SelectAllIcon from "@mui/icons-material/SelectAll";
import {
    Box,
    Tab,
    Tabs,
} from "@mui/material";
import { LayoutElement } from "@vertigis/web/components";
import type { LayoutElementProperties } from "@vertigis/web/components";
import { useWatchAndRerender } from "@vertigis/web/ui";
import React, { useEffect, useRef, useState } from "react";
import type { ReactElement } from "react";



import type DikeDesignerModel from "./DikeDesignerModel";
import {
    calculateVolume,
    cleanFeatureLayer,
    createDesigns,
    exportGraphicsLayerAsGeoJSON,
    initializeChart,
    initializeCrossSectionChart,
    setInputLineFromFeatureLayer,
    createCrossSection
} from "./Functions/DesignFunctions";
import ChartAndTablePanel from "./SubComponents/ChartAndTablePanel";
import CrossSectionChartPanel from "./SubComponents/CrossSectionChartPanel";
import DimensionsPanel from "./SubComponents/DimensionsPanel";
import EffectAnalysisPanel from "./SubComponents/EffectAnalysisPanel";


// import { SimpleWorker } from "./Workers/SimpleWorker"; // adjust path as needed
const DikeDesigner = (
    props: LayoutElementProperties<DikeDesignerModel>
): ReactElement => {
    const { model } = props;

    const chartContainerRef = useRef<HTMLDivElement | null>(null);
    const crossSectionChartContainerRef = useRef<HTMLDivElement | null>(null);

    const [mapLeftBorder, setMapLeftBorder] = useState(0);
    const [mapRightBorder, setMapRightBorder] = useState(window.innerWidth);
    const [activeTab, setActiveTab] = useState(0);
    const [isOverviewVisible, setIsOverviewVisible] = useState(false);
    const [isCrossSectionPanelVisible, setIsCrossSectionPanelVisible] = useState(false);
    const [loading, setLoading] = useState(false); // State to track loading status
    const [value, setValue] = React.useState(0);
    const [isLayerListVisible, setIsLayerListVisible] = useState(false);


    const handleChange = (event: React.SyntheticEvent, newValue: number) => {
        setValue(newValue);
    };

    const seriesRef = useRef<am5xy.LineSeries | null>(null);
    const chartSeriesRef = useRef<am5xy.LineSeries | null>(null);

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

    useEffect(() => {
        initializeCrossSectionChart(model, crossSectionChartContainerRef);
        return () => {
            if (model.crossSectionChartRoot) {
                model.crossSectionChartRoot.dispose();
                console.log("Cross-section chart disposed");
            }
        };
    }, [model, model.crossSectionChartRoot, crossSectionChartContainerRef, model.crossSectionChartData]);



    const handleDrawLine = async () => {
        await model.startDrawingLine();
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
        setIsCrossSectionPanelVisible(false);
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

    
    const handleCreateCrossSection = () => async () => {
        setIsOverviewVisible(false);
        setIsCrossSectionPanelVisible(true);
        await createCrossSection(model);
        chartSeriesRef.current?.data.setAll(model.crossSectionChartData);
        // set something for series ref...?
    }

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
        model.intersectingPanden = null;
        model.intersectingBomen = null;
        model.intersectingPercelen = null;
        cleanFeatureLayer(model.designLayer2D);
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
    useWatchAndRerender(model, "activeTab");
    useWatchAndRerender(model, "selectedDijkvakField");
    useWatchAndRerender(model, "chartData");
    useWatchAndRerender(model, "allChartData");
    useWatchAndRerender(model, "crossSectionChartData");
    useWatchAndRerender(model, "crossSectionChartData.length");


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
                        <Tab icon={<SelectAllIcon />} label="Afwegen" {...a11yProps(3)} />
                    </Tabs>
                </Box>
                <CustomTabPanel value={value} index={0}>
               <DimensionsPanel
                    model={model}
                    isLayerListVisible={isLayerListVisible}
                    isOverviewVisible={isOverviewVisible}
                    setSelectedLineLayerId={setSelectedLineLayerId}
                    handleDrawLine={handleDrawLine}
                    handleUploadGeoJSON={handleUploadGeoJSON}
                    handleSelectFromMap={handleSelectFromMap}
                    handleFileChange={handleFileChange}
                    handleClearGraphics={handleClearGraphics}
                    handleGridChange={handleGridChange}
                    handleExcelUpload={handleExcelUpload}
                    handleClearExcel={handleClearExcel}
                    handleOpenOverview={handleOpenOverview}
                    handleCreateDesign={handleCreateDesign}
                    handleExportGraphics={handleExportGraphics}
                    handleClearDesign={handleClearDesign}
                    handleCreateCrossSection={handleCreateCrossSection}
                    loading={loading}
                />
                </CustomTabPanel>
                <CustomTabPanel value={value} index={1}>
                    <EffectAnalysisPanel model={model} />
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
            {/* Paper for Cross Section Chart */}
            {isCrossSectionPanelVisible && (    
                <CrossSectionChartPanel
                    isCrossSectionPanelVisible={isCrossSectionPanelVisible}
                    setIsCrossSectionPanelVisible={setIsCrossSectionPanelVisible}
                    mapLeftBorder={mapLeftBorder}
                    mapRightBorder={mapRightBorder}
                    crossSectionChartContainerRef={crossSectionChartContainerRef}
                    model={model}
                />
            )}
        </LayoutElement>
    );
};

export default DikeDesigner;
