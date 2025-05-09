const fs = require("fs");
const path = require("path");

const buildFolder = "./build";

fs.readdir(buildFolder, (err, files) => {
    if (err) {
        console.error("Error reading the build folder:", err);
        return;
    }

    files
        .filter((file) => file.startsWith("main"))
        .forEach((file) => {
            const oldPath = path.join(buildFolder, file);
            const newPath = path.join(buildFolder, `wsrl-custom-${file}`);

            fs.rename(oldPath, newPath, (err) => {
                if (err) {
                    console.error(`Error renaming file ${file}:`, err);
                } else {
                    console.log(`Renamed ${file} to wsrl-custom-${file}`);
                }
            });
        });
});
