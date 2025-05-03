import CloseIcon from "@mui/icons-material/Close";
import {
    Paper,
    Typography,
    IconButton,
    Tabs,
    Tab,
    TableContainer,
    Table,
    TableHead,
    TableRow,
    TableCell,
    TableBody,
    TextField,
} from "@mui/material";
// import React, { useState } from "react";




interface ChartAndTablePanelProps {
    isOverviewVisible: boolean;
    setIsOverviewVisible: (visible: boolean) => void;
    activeTab: number;
    setActiveTab: (tab: number) => void;
    mapLeftBorder: number;
    mapRightBorder: number;
    chartContainerRef: React.RefObject<HTMLDivElement>;
    model: any;
    handleCellChange: (rowIndex: number, colKey: string, value: string) => void;
}

const ChartAndTablePanel: React.FC<ChartAndTablePanelProps> = ({
    isOverviewVisible,
    setIsOverviewVisible,
    activeTab,
    setActiveTab,
    mapLeftBorder,
    mapRightBorder,
    chartContainerRef,
    model,
    handleCellChange,
}) => {

    const handleSheetChange = (sheetName: string) => {
        model.activeSheet = sheetName; 
        model.chartData = model.allChartData[sheetName];
    }

    return (
        <Paper
            elevation={3}
            sx={{
                position: "fixed",
                bottom: 0,
                left: mapLeftBorder,
                width: mapRightBorder - mapLeftBorder,
                height: "50%",
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
                    onClick={() => setIsOverviewVisible(false)}
                    size="medium"
                    sx={{ color: "#ffffff" }}
                >
                    <CloseIcon />
                </IconButton>
            </Typography>
            <Tabs
                value={model.activeSheet}
                onChange={(event, newValue: string) => handleSheetChange(newValue)}
                indicatorColor="primary"
                textColor="primary"
                variant="scrollable"
                scrollButtons="auto"
            >
                {Object.keys(model.allChartData as object || {}).map((sheetName) => (
                    <Tab
                        key={sheetName}
                        label={sheetName}
                        value={sheetName}
                        sx={{
                            fontSize: "11px",
                            backgroundColor: model.activeSheet === sheetName ? "#e0e0e0" : "#f5f5f5", // Active tab is slightly darker
                            color: model.activeSheet === sheetName ? "#000" : "#555", // Active tab text is darker
                            "&:hover": {
                                backgroundColor: "#d6d6d6", // Hover effect
                            },
                        }}
                    />
                ))}
            </Tabs>
            <Tabs
                value={activeTab}
                onChange={(event, newValue: number) => setActiveTab(newValue)}
                indicatorColor="primary"
                textColor="primary"
                variant="fullWidth"
            >
                <Tab sx={{
                            fontSize: "11px",
                        }}
                             
                    label="Dwarsprofiel" />
                <Tab label="Invoerdata" />
            </Tabs>
            {activeTab === 0 && (
                <div
                    ref={chartContainerRef}
                    style={{
                        width: "100%",
                        height: "calc(100% - 95px)",
                        display: activeTab === 0 ? "block" : "none",
                    }}
                ></div>
            )}
            {activeTab === 1 && (
                <TableContainer
                    sx={{
                        height: "calc(100% - 95px)",
                        overflow: "auto",
                    }}
                >
                    <Table stickyHeader>
                        <TableHead>
                            <TableRow>
                                {model.chartData?.length > 0 &&
                                    Object.keys(model.chartData[0] as object).map((header) => (
                                        <TableCell sx={{ fontSize: "11px" }} key={header} align="center">
                                            {header.charAt(0).toUpperCase() + header.slice(1)}
                                        </TableCell>
                                    ))}
                            </TableRow>
                        </TableHead>
                        <TableBody>
                            {model.chartData?.map((row, rowIndex) => {
                                const rowKey = `afstand-${row.afstand ?? rowIndex}`;
                                return (
                                    <TableRow key={rowKey}>
                                        {Object.entries(row as object).map(([key, cell]) => (
                                            <TableCell key={`${rowKey}-${key}`} align="center">
                                                {typeof cell === "string" || typeof cell === "number" ? (
                                                    <TextField
                                                        value={cell}
                                                        onChange={(e) =>
                                                            handleCellChange(rowIndex as number, key, e.target.value)
                                                        }
                                                        variant="outlined"
                                                        size="small"
                                                    />
                                                ) : (
                                                    <span>Invalid Data</span> // Handle invalid data gracefully
                                                )}
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
    );
};

export default ChartAndTablePanel;


