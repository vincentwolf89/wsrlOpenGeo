import AddIcon from "@mui/icons-material/Add";
import AddBoxIcon from "@mui/icons-material/AddBox";
// import ClearIcon from "@mui/icons-material/Clear";
import CloseIcon from "@mui/icons-material/Close";
import DeleteIcon from "@mui/icons-material/Delete";
import DragIndicatorIcon from "@mui/icons-material/DragIndicator"; // Add this import
import EditIcon from "@mui/icons-material/Edit";
import FullscreenIcon from "@mui/icons-material/Fullscreen";
import FullscreenExitIcon from "@mui/icons-material/FullscreenExit";
import RemoveCircleOutlineIcon from "@mui/icons-material/RemoveCircleOutline";
import TableRowsIcon from "@mui/icons-material/TableRows";
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
  Dialog,
  DialogTitle,
  DialogContent,
  DialogActions,
} from "@mui/material";
import React, { useState } from "react";

interface ChartAndTablePanelProps {
  setdesignPanelVisible: (visible: boolean) => void;
  activeTab: number;
  setActiveTab: (tab: number) => void;
  mapLeftBorder: number;
  mapRightBorder: number;
  chartContainerRef: React.RefObject<HTMLDivElement>;
  model: any;
  handleCellChange: (rowIndex: number, colKey: string, value: string) => void;
  handleClearExcel: () => void;
  handleExcelUpload: (event: React.ChangeEvent<HTMLInputElement>) => void;
}

const ChartAndTablePanel: React.FC<ChartAndTablePanelProps> = ({
  setdesignPanelVisible,
  activeTab,
  setActiveTab,
  mapLeftBorder,
  mapRightBorder,
  chartContainerRef,
  model,
  handleCellChange,
  handleClearExcel,
  handleExcelUpload,
}) => {
  const [isMaximized, setIsMaximized] = useState(false);
  const [showNewTabDialog, setShowNewTabDialog] = useState(false);
  const [showDeleteTabDialog, setShowDeleteTabDialog] = useState(false);
  const [showRenameTabDialog, setShowRenameTabDialog] = useState(false); // Add this state
  const [newTabName, setNewTabName] = useState("");
  const [renameTabValue, setRenameTabValue] = useState(""); // Add this state
  const [draggedRowIndex, setDraggedRowIndex] = useState<number | null>(null);

  const handleSheetChange = (sheetName: string) => {
    const currentSheet = model.activeSheet;
    const currentData = model.chartData ? [...model.chartData] : [];
    model.allChartData[currentSheet] = currentData;

    model.activeSheet = sheetName;

    const newChartData = model.allChartData[sheetName] ? [...model.allChartData[sheetName]] : [];
    model.chartData = newChartData;

    console.log("Switched to sheet:", sheetName, model.chartData);
  };

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

  const handleToggleMaximize = () => {
    setIsMaximized(!isMaximized);
  };

  // Add new tab functionality
  const handleAddNewTab = () => {
    setShowNewTabDialog(true);
  };

  const handleCreateNewTab = () => {
    if (newTabName.trim() === "") {
      model.messages.commands.ui.displayNotification.execute({

        title: "Nieuw ontwerp",
        message: "Voer een naam in voorhet nieuwe ontwerp",
        type: "success",
      });

      return;
    }

    // Check if tab name already exists
    if (model.allChartData[newTabName]) {
      model.messages.commands.ui.displayNotification.execute({

        title: "Nieuw ontwerp",
        message: "Er bestaat al een tab met deze naam",
        type: "error",
      });
      return;
    }

    // Save current sheet data
    const currentSheet = model.activeSheet;
    const currentData = model.chartData ? [...model.chartData] : [];
    model.allChartData[currentSheet] = currentData;

    // Create new empty sheet with default structure
    const newSheetData = [
      {
        locatie: "",
        afstand: "",
        hoogte: "",
      }
    ];

    model.allChartData[newTabName] = newSheetData;
    model.activeSheet = newTabName;
    model.chartData = [...newSheetData];

    // Close dialog and reset
    setShowNewTabDialog(false);
    setNewTabName("");

    console.log("Created new tab:", newTabName);
  };

  const handleCancelNewTab = () => {
    setShowNewTabDialog(false);
    setNewTabName("");
  };

  // Delete tab functionality
  const handleDeleteCurrentTab = () => {
    const allSheets = Object.keys(model.allChartData as Record<string, any[]> || {});

    // Don't allow deleting if it's the only tab
    if (allSheets.length <= 1) {
      model.messages.commands.ui.displayNotification.execute({
        title: "Verwijder tab",
        message: "Je kunt de laatste tab niet verwijderen",
        type: "error",
      });
      return;
    }

    setShowDeleteTabDialog(true);
  };

  const handleConfirmDeleteTab = () => {
    const currentSheet = model.activeSheet;
    const allSheets = Object.keys(model.allChartData as Record<string, any[]> || {});

    // Remove the current sheet from allChartData
    delete model.allChartData[currentSheet];

    // Switch to another available sheet
    const remainingSheets = allSheets.filter(sheet => sheet !== currentSheet);
    const newActiveSheet = remainingSheets[0];

    model.activeSheet = newActiveSheet;
    model.chartData = model.allChartData[newActiveSheet] ? [...model.allChartData[newActiveSheet]] : [];

    setShowDeleteTabDialog(false);

    console.log("Deleted tab:", currentSheet, "Switched to:", newActiveSheet);
  };

  const handleCancelDeleteTab = () => {
    setShowDeleteTabDialog(false);
  };

  // Add rename tab functionality
  const handleRenameCurrentTab = () => {
    setRenameTabValue(model.activeSheet as string); // Pre-fill with current name
    setShowRenameTabDialog(true);
  };

  const handleConfirmRenameTab = () => {
    if (renameTabValue.trim() === "") {
      model.messages.commands.ui.displayNotification.execute({
        title: "Hernoem tab",
        message: "Voer een naam in voor de tab",
        type: "error",
      });
      return;
    }

    // Check if the new name already exists (and it's not the current name)
    if (renameTabValue !== model.activeSheet && model.allChartData[renameTabValue]) {
      model.messages.commands.ui.displayNotification.execute({
        title: "Hernoem tab",
        message: "Er bestaat al een tab met deze naam",
        type: "error",
      });
      return;
    }

    // If the name hasn't changed, just close the dialog
    if (renameTabValue === model.activeSheet) {
      setShowRenameTabDialog(false);
      setRenameTabValue("");
      return;
    }

    const oldName = model.activeSheet;
    const newName = renameTabValue.trim();

    // Save current data with the old name
    const currentData = model.chartData ? [...model.chartData] : [];
    model.allChartData[oldName] = currentData;

    // Create new entry with new name
    model.allChartData[newName] = model.allChartData[oldName];

    // Delete old entry
    delete model.allChartData[oldName];

    // Update active sheet name
    model.activeSheet = newName;

    // Close dialog and reset
    setShowRenameTabDialog(false);
    setRenameTabValue("");

    model.messages.commands.ui.displayNotification.execute({
      title: "Hernoem tab",
      message: `Tab hernoemd van "${oldName}" naar "${newName}"`,
      type: "success",
    });

    console.log("Renamed tab from:", oldName, "to:", newName);
  };

  const handleCancelRenameTab = () => {
    setShowRenameTabDialog(false);
    setRenameTabValue("");
  };

  // Simple drag and drop handlers
  const handleDragStart = (e: React.DragEvent, index: number) => {
    setDraggedRowIndex(index);
    e.dataTransfer.effectAllowed = "move";
    // Visual feedback will be handled by the sx prop based on draggedRowIndex state
  };

  const handleDragEnd = (e: React.DragEvent) => {
    setDraggedRowIndex(null);
    // Visual feedback reset handled by state change
  };

  const handleDragOver = (e: React.DragEvent) => {
    e.preventDefault();
    e.dataTransfer.dropEffect = "move";
  };

  const handleDrop = (e: React.DragEvent, dropIndex: number) => {
    e.preventDefault();
    
    if (draggedRowIndex === null || draggedRowIndex === dropIndex) {
      return;
    }

    // Reorder the array
    const newChartData = [...model.chartData];
    const draggedItem = newChartData[draggedRowIndex];
    
    // Remove the dragged item
    newChartData.splice(draggedRowIndex, 1);
    
    // Insert at new position
    newChartData.splice(dropIndex, 0, draggedItem);
    
    // Update the model
    model.chartData = newChartData;
    
    console.log(`Moved row from ${draggedRowIndex} to ${dropIndex}`);
  };

  return (
    <>
      <Paper
        elevation={3}
        sx={{
          position: "fixed",
          bottom: 0,
          left: mapLeftBorder,
          width: mapRightBorder - mapLeftBorder,
          height: isMaximized ? "100vh" : "50%",
          zIndex: 10,
          p: 0,
          borderRadius: "5px",
          backgroundColor: "#ffffff",
          boxShadow: "0px 6px 15px rgba(0, 0, 0, 0.15)",
          display: "flex",
          flexDirection: "column",
        }}
      >
        {/* Header with maximize button */}
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

          <Box sx={{ display: "flex", alignItems: "center" }}>
            <IconButton
              aria-label="maximize"
              onClick={handleToggleMaximize}
              size="medium"
              sx={{ color: "#ffffff", marginRight: 1 }}
            >
              {isMaximized ? <FullscreenExitIcon /> : <FullscreenIcon />}
            </IconButton>
            <IconButton
              aria-label="close"
              onClick={() => setdesignPanelVisible(false)}
              size="medium"
              sx={{ color: "#ffffff" }}
            >
              <CloseIcon />
            </IconButton>
          </Box>
        </Typography>

        {/* Buttons row (Upload / Remove / Nieuw ontwerp) */}
        <Box
          sx={{
            display: "flex",
            alignItems: "center",
            justifyContent: "space-between",
            flexShrink: 0,
            gap: 1,
            p: 1,
            backgroundColor: "#fafafa",
            borderBottom: "1px solid rgba(0,0,0,0.06)",
          }}
        >
          <Box sx={{ display: "flex", gap: 1, alignItems: "center" }}>
            <Button
              variant="contained"
              size="medium"
              component="label"
              startIcon={<TableRowsIcon />}
              color="primary"
              // sx={{ textTransform: "none" }}
            >
              Upload ontwerpen (Excel)
              <input
                type="file"
                accept=".xlsx, .xls"
                hidden
                onChange={handleExcelUpload}
                
              />
            </Button>

            {/* <Button
              disabled={!model.chartData?.length}
              variant="outlined"
              size="small"
              color="secondary"
              startIcon={<ClearIcon />}
              onClick={handleClearExcel}
              sx={{ textTransform: "none" }}
            >
              Verwijder ontwerpen
            </Button> */}

            <Button
              variant="contained"
              size="medium"
              color="secondary"
              startIcon={<AddBoxIcon />}
              onClick={handleAddNewTab}
              // sx={{ textTransform: "none" }}
            >
              Nieuw ontwerp toevoegen
            </Button>
          </Box>

          {/* Tab action icons on the right for quick access */}
          <Box sx={{ display: "flex", gap: 0.5, alignItems: "center" }}>
            <IconButton
              onClick={handleRenameCurrentTab}
              size="medium"
              sx={{
                color: "#1976d2",
                "&:hover": { backgroundColor: "#e3f2fd" },
              }}
              title="Huidig ontwerp hernoemen"
            >
              <EditIcon />
            </IconButton>

            <IconButton
              onClick={handleDeleteCurrentTab}
              size="medium"
              sx={{
                color: "#d32f2f",
                "&:hover": { backgroundColor: "#ffebee" },
              }}
              title="Huidig ontwerp verwijderen"
              disabled={
                Object.keys(model.allChartData as Record<string, any[]> || {})
                  .length <= 1
              }
            >
              <RemoveCircleOutlineIcon />
            </IconButton>
          </Box>
        </Box>

        {/* Tabs below the buttons */}
        <Tabs
          value={model.activeSheet}
          onChange={(event, newValue: string) => handleSheetChange(newValue)}
          indicatorColor="primary"
          textColor="primary"
          variant="scrollable"
          scrollButtons="auto"
          sx={{
            flexShrink: 0,
            backgroundColor: "#fff",
          }}
        >
          {Object.keys(model.allChartData as object || {}).map((sheetName) => (
            <Tab
              key={sheetName}
              label={sheetName}
              value={sheetName}
              sx={{
                fontSize: "11px",
                backgroundColor:
                  model.activeSheet === sheetName ? "#e0e0e0" : "#f5f5f5",
                color: model.activeSheet === sheetName ? "#000" : "#555",
                "&:hover": { backgroundColor: "#d6d6d6" },
                textTransform: "none",
                minHeight: 36,
                px: 1.5,
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
                    <TableCell align="center" sx={{ fontSize: "11px", width: "40px" }}>
                      {/* Drag handle column header */}
                    </TableCell>
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
                    const rowKey = `row-${rowIndex}`;
                    return (
                      <TableRow
                        key={rowKey}
                        draggable
                        onDragStart={(e) => handleDragStart(e, rowIndex as number)}
                        onDragEnd={handleDragEnd}
                        onDragOver={handleDragOver}
                        onDrop={(e) => handleDrop(e, rowIndex as number)}
                        sx={{
                          cursor: "move",
                          "&:hover": {
                            backgroundColor: "#f9f9f9",
                          },
                          backgroundColor: draggedRowIndex === rowIndex ? "#e3f2fd" : "inherit",
                          opacity: draggedRowIndex === rowIndex ? 0.5 : 1, // Add this line
                        }}
                      >
                        {/* Drag handle column */}
                        <TableCell align="center" sx={{ width: "40px" }}>
                          <DragIndicatorIcon
                            sx={{
                              color: "#999",
                              fontSize: "18px",
                              cursor: "grab",
                              "&:hover": { color: "#666" },
                              "&:active": { cursor: "grabbing" },
                            }}
                          />
                        </TableCell>

                        {/* Data columns */}
                        {Object.entries(row as object || {}).map(([key, cell], colIndex) => (
                          <TableCell key={`${rowKey}-${key}`} align="center">
                            {colIndex === 0 ? (
                              <Select
                                value={cell}
                                onChange={(e) =>
                                  handleCellChange(rowIndex as number, key, e.target.value as string)
                                }
                                variant="outlined"
                                size="small"
                                fullWidth
                                onMouseDown={(e) => e.stopPropagation()} // Prevent drag when clicking select
                              >
                                {model.dwpLocations.map((option) => (
                                  <MenuItem key={option} value={option}>
                                    {option}
                                  </MenuItem>
                                ))}
                              </Select>
                            ) : typeof cell === "string" || typeof cell === "number" ? (
                              <TextField
                                defaultValue={isNaN(cell as number) ? "" : cell}
                                onBlur={(e) =>
                                  handleCellChange(rowIndex as number, key, e.target.value)
                                }
                                variant="outlined"
                                size="small"
                                onMouseDown={(e) => e.stopPropagation()} // Prevent drag when clicking text field
                              />
                            ) : (
                              <span>Invalid Data</span>
                            )}
                          </TableCell>
                        ))}

                        {/* Actions column */}
                        <TableCell align="center">
                          <IconButton
                            color="error"
                            size="small"
                            onClick={() => handleRemoveRow(rowIndex as number)}
                            onMouseDown={(e) => e.stopPropagation()} // Prevent drag when clicking delete
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

      {/* New Tab Dialog */}
      <Dialog
        open={showNewTabDialog}
        onClose={handleCancelNewTab}
        maxWidth="sm"
        fullWidth
      >
        <DialogTitle>Nieuw ontwerp toevoegen</DialogTitle>
        <DialogContent>
          <TextField
            autoFocus
            margin="dense"
            label="Ontwerp naam"
            type="text"
            fullWidth
            variant="outlined"
            value={newTabName}
            onChange={(e) => setNewTabName(e.target.value)}
            onKeyPress={(e) => {
              if (e.key === 'Enter') {
                handleCreateNewTab();
              }
            }}
          />
        </DialogContent>
        <DialogActions>
          <Button onClick={handleCancelNewTab}>Annuleren</Button>
          <Button onClick={handleCreateNewTab} variant="contained" color="primary">
            Maken
          </Button>
        </DialogActions>
      </Dialog>

      {/* Rename Tab Dialog */}
      <Dialog
        open={showRenameTabDialog}
        onClose={handleCancelRenameTab}
        maxWidth="sm"
        fullWidth
      >
        <DialogTitle>Tab Hernoemen</DialogTitle>
        <DialogContent>
          <TextField
            autoFocus
            margin="dense"
            label="Naam nieuwe ontwerp"
            type="text"
            fullWidth
            variant="outlined"
            value={renameTabValue}
            onChange={(e) => setRenameTabValue(e.target.value)}
            onKeyPress={(e) => {
              if (e.key === 'Enter') {
                handleConfirmRenameTab();
              }
            }}
          />
        </DialogContent>
        <DialogActions>
          <Button onClick={handleCancelRenameTab}>Annuleren</Button>
          <Button onClick={handleConfirmRenameTab} variant="contained" color="primary">
            Hernoemen
          </Button>
        </DialogActions>
      </Dialog>

      {/* Delete Tab Confirmation Dialog */}
      <Dialog
        open={showDeleteTabDialog}
        onClose={handleCancelDeleteTab}
        maxWidth="sm"
        fullWidth
      >
        <DialogTitle>Tab Verwijderen</DialogTitle>
        <DialogContent>
          <Typography>
            {`Weet je zeker dat je de tab "${model.activeSheet}" wilt verwijderen? Alle data in deze tab gaat verloren.`}
          </Typography>
        </DialogContent>
        <DialogActions>
          <Button onClick={handleCancelDeleteTab}>Annuleren</Button>
          <Button onClick={handleConfirmDeleteTab} variant="contained" color="error">
            Verwijderen
          </Button>
        </DialogActions>
      </Dialog>
    </>
  );
};

export default ChartAndTablePanel;


