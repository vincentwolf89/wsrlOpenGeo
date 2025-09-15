import ClearIcon from "@mui/icons-material/Clear";
import CloudDownloadIcon from "@mui/icons-material/CloudDownload";
import EditIcon from "@mui/icons-material/Edit";
import FilterIcon from "@mui/icons-material/Filter";
import InsightsIcon from '@mui/icons-material/Insights';
import MapIcon from "@mui/icons-material/Map";
import PlayCircleFilledWhiteIcon from "@mui/icons-material/PlayCircleFilledWhite";
// import TableRowsIcon from "@mui/icons-material/TableRows";
import UploadFileIcon from "@mui/icons-material/UploadFile";
import {
    Stack,
    ButtonGroup,
    Button,
    FormControl,
    InputLabel,
    Select,
    MenuItem,
    TableContainer,
    Table,
    TableBody,
    TableRow,
    TableCell,
    LinearProgress,
    TextField,
} from "@mui/material";
import React from "react";

import { stackStyle } from "../../styles";


interface DimensionsPanelProps {
    model: any;
    isLayerListVisible: boolean;
    setSelectedLineLayerId: (id: string) => void;
    handleUploadGeoJSON: () => void;
    handleSelectFromMap: () => void;
    handleFileChange: (event: React.ChangeEvent<HTMLInputElement>) => void;
    handleClearGraphics: () => void;
    handleGridChange: (event: React.ChangeEvent<HTMLInputElement>) => void;
    handleExcelUpload: (event: React.ChangeEvent<HTMLInputElement>) => void;
    handleClearExcel: () => void;
    handleOpenOverview: () => void;
    handleCreateCrossSection: () => () => void;
    handleCreateDesign: () => void;
    handleExportGraphics: () => void;
    handleClearDesign: () => void;
    loading: boolean;
}

const DimensionsPanel: React.FC<DimensionsPanelProps> = ({
    model,
    isLayerListVisible,
    setSelectedLineLayerId,
    handleUploadGeoJSON,
    handleSelectFromMap,
    handleFileChange,
    handleClearGraphics,
    handleGridChange,
    handleExcelUpload,
    handleClearExcel,
    handleOpenOverview,
    handleCreateCrossSection,
    handleCreateDesign,
    handleExportGraphics,
    handleClearDesign,
    loading,
}) => {

    const handleCreateLine = () => {
            model.startDrawingLine(model.graphicsLayerLine);
    };

    return (
        <Stack spacing={1}>
            <Stack spacing={2} sx={stackStyle}>
                <ButtonGroup fullWidth>
                    <Button
                        disabled={!model.sketchViewModel}
                        color="primary"
                        onClick={handleCreateLine}
                        startIcon={<EditIcon />}
                        variant="contained"
                        sx={{
                            flexDirection: "column",
                            padding: "8px 4px",
                            fontSize: "9px",
                        }}
                    >
                        Teken referentielijn
                    </Button>
                    <Button
                        color="primary"
                        onClick={handleUploadGeoJSON}
                        startIcon={<UploadFileIcon />}
                        variant="contained"
                        disabled={!model.map}
                        sx={{
                            flexDirection: "column",
                            padding: "8px 4px",
                            fontSize: "9px",
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
                            flexDirection: "column",
                            padding: "8px 4px",
                            fontSize: "9px",
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
                                sx={{ fontSize: "11px" }}
                            >
                                Ontwerplijn
                            </InputLabel>
                            <Select
                                value={model.selectedLineLayerId}
                                onChange={(e) => setSelectedLineLayerId(e.target.value as string)}
                                displayEmpty
                                fullWidth
                                variant="outlined"
                                sx={{
                                    fontSize: "11px",
                                }}
                            >
                                {model.lineFeatureLayers.map((layer) => (
                                    <MenuItem
                                        key={layer.id}
                                        value={layer.id}
                                        sx={{ fontSize: "11px" }}
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
                                    sx={{ fontSize: "11px" }}
                                >
                                    Dijkvak-id veld
                                </InputLabel>
                                <Select
                                    value={model.selectedDijkvakField || ""}
                                    onChange={(e) => {
                                        model.selectedDijkvakField = e.target.value;
                                    }}
                                    displayEmpty
                                    fullWidth
                                    variant="outlined"
                                    sx={{
                                        fontSize: "11px",
                                    }}
                                >
                                    {model.selectedDijkvakLayerFields.map((field) => (
                                        <MenuItem
                                            key={field}
                                            value={field}
                                            sx={{ fontSize: "11px" }}
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

            <Stack spacing={1} sx={stackStyle}>
                {/* Hidden input for GeoJSON upload */}
                <input
                    id="geojson-upload"
                    type="file"
                    accept=".geojson"
                    hidden
                    onChange={handleFileChange}
                />
                {/* <Button
                    variant="contained"
                    component="label"
                    startIcon={<TableRowsIcon />}
                    color="primary"
                    fullWidth
                >
                    Upload ontwerpen (Excel)
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
                    Verwijder ontwerpen
                </Button> */}
            </Stack>
            <Stack spacing={1.5} sx={stackStyle}>
                <Button
                    variant="contained"
                    color="primary"
                    startIcon={<FilterIcon />}
                    onClick={handleOpenOverview}
                    fullWidth
                    disabled={model.designPanelVisible}
                >
                    Open 2D-ontwerpen
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

            <Stack spacing={1.5} sx={stackStyle}>
                <Button
                    // disabled={!model.chartData?.length}
                    variant="contained"
                    color="primary"
                    startIcon={<InsightsIcon />}
                    onClick={handleCreateCrossSection()}
                    fullWidth
                >
                    Controleer dwarsprofiel
                </Button>
                {/* <Button
                    // disabled={!model.chartData?.length}
                    variant="contained"
                    color="primary"
                    startIcon={<ClearIcon />}
                    onClick={handleRemoveTalud()}
                    fullWidth
                >
                    Verwijder taludlijn
                </Button> */}
            </Stack>
        </Stack>
    );
};

export default DimensionsPanel;