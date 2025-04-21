export const SimpleWorker = `
self.onmessage = function (e) {
    const { extent, gridSize, elevationData } = e.data;

    const pointCoordsForVolume = [];
    const groundPoints = [];

    for (let x = extent.xmin; x <= extent.xmax; x += gridSize) {
        for (let y = extent.ymin; y <= extent.ymax; y += gridSize) {
            const key = \`\${x},\${y}\`;
            const elevation = elevationData[key];

            if (elevation !== undefined) {
                pointCoordsForVolume.push([x, y, elevation]);
                groundPoints.push({ x, y });
            }
        }
    }

    self.postMessage({ pointCoordsForVolume, groundPoints });
};

//# sourceURL=simpleWorker.js
`;