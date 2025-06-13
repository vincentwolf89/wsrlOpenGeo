import AddIcon from "@mui/icons-material/Add";
import CloseIcon from "@mui/icons-material/Close";
import DeleteIcon from "@mui/icons-material/Delete";
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
  Box,
  Select,
  MenuItem,
  Button,
} from "@mui/material";
// import { useEffect } from "react";
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
    const currentSheet = model.activeSheet;
    const currentData = model.chartData ? [...model.chartData] : [];
    model.allChartData[currentSheet] = currentData;

    model.activeSheet = sheetName;

    const newChartData = model.allChartData[sheetName] ? [...model.allChartData[sheetName]] : [];
    model.chartData = newChartData;

    console.log("Switched to sheet:", sheetName, model.chartData);
};
  
    // useEffect(() => {
    //     console.log("ChartAndTablePanel mounted");
    //     return () => {
    //         console.log("ChartAndTablePanel unmounted");
    //     };
    // }, []);

  const handleAddRow = () => {
    const newRow = {
      locatie: "",
      afstand: "",
      hoogte: "",
    };
    model.chartData = [...model.chartData, newRow];
  };


  const handleRemoveRow = (rowIndex: number) => {
    model.chartData = model.chartData.filter((_, index) => index !== rowIndex);
  };

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
        p: 0,
        borderRadius: "5px",
        backgroundColor: "#ffffff",
        boxShadow: "0px 6px 15px rgba(0, 0, 0, 0.15)",
        display: "flex",
        flexDirection: "column",
      }}
    >
      <Typography
        variant="h6"
        sx={{
          fontWeight: "bold",
          color: "#ffffff",
          backgroundColor: "#1976d2",
          px: 2,
          py: 1,
          fontSize: "12px",
          borderTopLeftRadius: "4px",
          borderTopRightRadius: "4px",
          display: "flex",
          justifyContent: "space-between",
          alignItems: "center",
          flexShrink: 0,
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

      {/* First Tab Bar: Sheet Selection */}
      <Tabs
        value={model.activeSheet}
        onChange={(event, newValue: string) => handleSheetChange(newValue)}
        indicatorColor="primary"
        textColor="primary"
        variant="scrollable"
        scrollButtons="auto"
        sx={{ flexShrink: 0 }}
      >
        {Object.keys(model.allChartData as object || {}).map((sheetName) => (
          <Tab
            key={sheetName}
            label={sheetName}
            value={sheetName}
            sx={{
              fontSize: "11px",
              backgroundColor: model.activeSheet === sheetName ? "#e0e0e0" : "#f5f5f5",
              color: model.activeSheet === sheetName ? "#000" : "#555",
              "&:hover": { backgroundColor: "#d6d6d6" },
            }}
          />
        ))}
      </Tabs>

      {/* Second Tab Bar: Content Type */}
      <Tabs
        value={activeTab}
        onChange={(event, newValue: number) => setActiveTab(newValue)}
        indicatorColor="primary"
        textColor="primary"
        variant="fullWidth"
        sx={{ flexShrink: 0 }}
      >
        <Tab label="Dwarsprofiel" sx={{ fontSize: "11px" }} />
        <Tab label="Invoerdata" />
      </Tabs>

      {/* Content Area */}
      {activeTab === 0 && (
        <Box
          ref={chartContainerRef}
          sx={{
            flexGrow: 1,
            width: "100%",
            overflow: "hidden",
          }}
        />
      )}

      {activeTab === 1 && (
        <>
          {/* Add and Remove Row Buttons */}
          <Box
            sx={{
              display: "flex",
              justifyContent: "space-between",
              padding: "8px",
              backgroundColor: "#f5f5f5",
            }}
          >
            <Button
              variant="contained"
              color="primary"
              startIcon={<AddIcon />}
              onClick={handleAddRow}
            >
              Voeg nieuwe rij toe
            </Button>
          </Box>

          <TableContainer
           key={model.activeSheet}
            sx={{
              flexGrow: 1,
              overflow: "auto",
            }}
          >
            <Table stickyHeader>
              <TableHead>
                <TableRow>
                  {model.chartData?.length > 0 &&
                    Object.keys(model.chartData[0] as object || {}).map((header) => (
                      <TableCell key={header} align="center" sx={{ fontSize: "11px" }}>
                        {header.charAt(0).toUpperCase() + header.slice(1)}
                      </TableCell>
                    ))}
                  <TableCell align="center" sx={{ fontSize: "11px" }}>
                    Acties
                  </TableCell>
                </TableRow>
              </TableHead>
              <TableBody>
                {model.chartData?.map((row, rowIndex) => {
                  const rowKey = `afstand-${row.afstand ?? rowIndex}`;
                  return (
                    <TableRow key={row.id || rowKey}>
                      {Object.entries(row as object || {}).map(([key, cell], colIndex) => (
                        <TableCell key={`${rowKey}-${key}`} align="center">
                          {colIndex === 0 ? ( // Check if it's the first column
                            <Select
                              value={cell}
                              onChange={(e) =>
                                handleCellChange(rowIndex as number, key, e.target.value as string)
                              }
                              variant="outlined"
                              size="small"
                              fullWidth
                            >
                              {model.dwpLocations.map((option) => (
                                <MenuItem key={option} value={option}>
                                  {option}
                                </MenuItem>
                              ))}
                            </Select>
                          ) : typeof cell === "string" || typeof cell === "number" ? (
                            <TextField
                              defaultValue={isNaN(cell as number) ? "" : cell} // Replace NaN with an empty string
                              // value={isNaN(cell as number) ? "" : cell} // Replace NaN with an empty string
                              // onChange={(e) =>
                              //   handleCellChange(rowIndex as number, key, e.target.value)
                              // }
                              onBlur={(e) =>
                                handleCellChange(rowIndex as number, key, e.target.value)
                              }
                              variant="outlined"
                              size="small"
                            />
                          ) : (
                            <span>Invalid Data</span>
                          )}
                        </TableCell>
                      ))}
                      <TableCell align="center">
                        <IconButton
                          color="error"
                          size="small"
                          onClick={() => handleRemoveRow(rowIndex as number)}
                        >
                          <DeleteIcon />
                        </IconButton>
                      </TableCell>
                    </TableRow>
                  );
                })}
              </TableBody>
            </Table>
          </TableContainer>
        </>
      )}
    </Paper>

  );
};

export default ChartAndTablePanel;


