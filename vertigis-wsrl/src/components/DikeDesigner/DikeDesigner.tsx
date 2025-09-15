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

    const prevDeps = useRef<any>({});

    const chartContainerRef = useRef<HTMLDivElement | null>(null);
    const crossSectionChartContainerRef = useRef<HTMLDivElement | null>(null);

    const [mapLeftBorder, setMapLeftBorder] = useState(0);
    const [mapRightBorder, setMapRightBorder] = useState(window.innerWidth);
    const [activeTab, setActiveTab] = useState(0);
    const [loading, setLoading] = useState(false); // State to track loading status
    const [value, setValue] = React.useState(0);
    const [isLayerListVisible, setIsLayerListVisible] = useState(false);

    function setcrossSectionPanelVisible(value: boolean) {
        model.crossSectionPanelVisible = value;
        if (!value) {
            model.userLinePoints = [];
        }
    }

    function setdesignPanelVisible(value: boolean) {
        model.designPanelVisible = value;
        model.crossSectionPanelVisible = false;
    }



    const handleChange = (event: React.SyntheticEvent, newValue: number) => {
        setValue(newValue);
    };

    const seriesRef = useRef<am5xy.LineSeries | null>(null);
    const chartSeriesRef = useRef<am5xy.LineSeries | null>(null);
    const meshSeriesRef = useRef<am5xy.LineSeries | null>(null);
    const userSeriesRef = useRef<am5xy.LineSeries | null>(null);

    const mapResizeObserver = () => {
        const mapElement = model.mapElement;
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
        const disconnectObserver = mapResizeObserver();
        return () => {
            if (disconnectObserver) disconnectObserver();
        };
    }, ); 

    useEffect(() => {
        initializeChart(model, activeTab, chartContainerRef, seriesRef);
        return () => {
            if (model.chartRoot) {
                model.chartRoot.dispose();
                console.log("Chart disposed");
            }
        }
    }, [model.overviewVisible, model, activeTab, chartContainerRef, model.chartData]);

    useEffect(() => {
        // Compare and log changes
        if (prevDeps.current.model !== model) {
            console.log("model changed");
        }
        if (prevDeps.current.crossSectionChartRoot !== model.crossSectionChartRoot) {
            console.log("model.crossSectionChartRoot changed");
        }
        if (prevDeps.current.crossSectionChartContainerRef !== crossSectionChartContainerRef) {
            console.log("crossSectionChartContainerRef changed");
        }
        if (prevDeps.current.crossSectionChartData !== model.crossSectionChartData) {
            console.log("model.crossSectionChartData changed");
        }
        if (prevDeps.current.meshSeriesData !== model.meshSeriesData) {
            console.log("model.meshSeriesData changed");
        }

        // Update previous values
        prevDeps.current = {
            model,
            crossSectionChartRoot: model.crossSectionChartRoot,
            crossSectionChartContainerRef,
            crossSectionChartData: model.crossSectionChartData,
            meshSeriesData: model.meshSeriesData,
        };

        // ...your effect logic...
        initializeCrossSectionChart(model, crossSectionChartContainerRef, {
            chartSeriesRef,
            meshSeriesRef,
            userSeriesRef
        });
        return () => {
            if (model.crossSectionChartRoot) {
                model.crossSectionChartRoot.dispose();
                console.log("Cross-section chart disposed");
            }
        };
    }, [model, crossSectionChartContainerRef, model.crossSectionChartData, model.meshSeriesData]);



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
        setdesignPanelVisible(true);
        setcrossSectionPanelVisible(false);
        const updatedData = [...model.chartData];
        model.chartData = updatedData
        seriesRef.current?.data.setAll(model.chartData);
    };

    const handleClearExcel = () => {
        model.chartData = [];
    };
    const handleExcelUpload = (event: React.ChangeEvent<HTMLInputElement>) => {
        setdesignPanelVisible(true); // Close the overview when uploading a new Excel file
        model.handleExcelUpload(event);

    }

    const handleCreateDesign = async () => {

        setLoading(true); // Show loader
        try {
            createDesigns(model).then(() => {
                console.log("Designs created");
                calculateVolume(model).then(() => {
                    console.log("Volume calculated");
                }).catch((error) => {
                    console.error("Error calculating volume:", error);
                });
            }).catch((error) => {
                console.error("Error creating designs:", error);
            });
            
            // console.log("All done...");
        } catch (error) {
            console.error("Error during design creation or volume calculation:", error);
        } finally {
            setLoading(false); // Hide loader
        }
    };


    const handleCreateCrossSection = () => async () => {
        setdesignPanelVisible(false);
        await createCrossSection(model);
    }

    const handleClearDesign = () => {
        model.meshes = []
        model.offsetGeometries = []
        model.graphicsLayerTemp.removeAll();
        model.graphicsLayerMesh.removeAll();
        model.mergedMesh = null;
        model.totalVolumeDifference = null;
        model.excavationVolume = null;
        model.fillVolume = null;
        model.intersectingPanden = null;
        model.intersectingBomen = null;
        model.intersectingPercelen = null;
        model.userLinePoints = [];
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
    useWatchAndRerender(model, "crossSectionPanelVisible");
    useWatchAndRerender(model, "designPanelVisible");
    useWatchAndRerender(model, "mapElement");

    // useWatchAndRerender(model, "meshSeriesData");
    // useWatchAndRerender(model, "meshSeriesData.length");


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
        <LayoutElement {...props} style={{ width: "100%", overflowY: "scroll" }}>
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
                        setSelectedLineLayerId={setSelectedLineLayerId}
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
            {model.designPanelVisible && (() => {
                // Initialize empty data if needed
                if (!model.chartData || model.chartData.length === 0) {
                    model.initializeEmptyChartData();
                }
                return (
                    <ChartAndTablePanel
                        setdesignPanelVisible={setdesignPanelVisible}
                        activeTab={activeTab}
                        setActiveTab={setActiveTab}
                        mapLeftBorder={mapLeftBorder}
                        mapRightBorder={mapRightBorder}
                        chartContainerRef={chartContainerRef}
                        model={model}
                        handleCellChange={handleCellChange}
                        handleClearExcel={handleClearExcel}
                        handleExcelUpload={handleExcelUpload}
                    />
                );
            })()}
            {/* Paper for Cross Section Chart */}
            {model.crossSectionPanelVisible && (
                <CrossSectionChartPanel
                    setcrossSectionPanelVisible={setcrossSectionPanelVisible}
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
