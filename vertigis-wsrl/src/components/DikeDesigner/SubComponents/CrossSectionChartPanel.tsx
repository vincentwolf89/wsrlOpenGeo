// import AddIcon from "@mui/icons-material/Add";
import CloseIcon from "@mui/icons-material/Close";
// import DeleteIcon from "@mui/icons-material/Delete";
import {
  Paper,
  Typography,
  IconButton,
//   Tabs,
//   Tab,
//   TableContainer,
//   Table,
//   TableHead,
//   TableRow,
//   TableCell,
//   TableBody,
//   TextField,
  Box,
//   Select,
//   MenuItem,
//   Button,
} from "@mui/material";
import { useEffect } from "react";
// import React, { useState } from "react";




interface CrossSectionChartPanelProps {
  setcrossSectionPanelVisible: (visible: boolean) => void;
  mapLeftBorder: number;
  mapRightBorder: number;
  crossSectionChartContainerRef: React.RefObject<HTMLDivElement>;
  model: any;
}

const CrossSectionChartPanel: React.FC<CrossSectionChartPanelProps> = ({
  setcrossSectionPanelVisible,
  mapLeftBorder,
  mapRightBorder,
  crossSectionChartContainerRef,
  model,
}) => {
    useEffect(() => {
      console.log("Component mounted", crossSectionChartContainerRef.current);
      return () => {
        console.log("Component unmounted");
      };
    }, [crossSectionChartContainerRef]);

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
        Dwarsprofiel overzicht
        <IconButton
          aria-label="close"
          onClick={() => setcrossSectionPanelVisible(false)}
          size="medium"
          sx={{ color: "#ffffff" }}
        >
          <CloseIcon />
        </IconButton>
      </Typography>
      {/* Content Area */}

        <Box
          ref={crossSectionChartContainerRef}
          sx={{
            flexGrow: 1,
            width: "100%",
            overflow: "hidden",
          }}

        />
      
    </Paper>

  );
};

export default CrossSectionChartPanel;


