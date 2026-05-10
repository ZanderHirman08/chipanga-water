# Chipanga QField Project — Zander Setup Guide

This folder is the source-of-truth for the Chipanga A water + gardens data collection project. You'll build a QField package here and hand it to Charlie. When he sends edits back, you re-open the same `.gpkg` and you have authoritative data.

## What's in this folder

| File | Purpose |
|---|---|
| `chipanga.gpkg` | Master GeoPackage — 7 feature layers (school buildings, garden plots, fence areas, solar array, water towers, infrastructure points, water pipelines). School buildings already pre-filled with the 6 GPS coords you sent. |
| `setup_chipanga_project.py` | One-shot PyQGIS script. Run inside QGIS to wire up forms, dropdowns, photo widget, satellite basemap, styling, and save `chipanga.qgz`. |
| `README_zander_setup.md` | This file. |
| `README_charlie_field.md` | Field guide for Charlie. Print or send via WhatsApp. |
| `chipanga_old.gpkg` | Backup of the original School_Buildings file. Ignore. |

## One-time desktop setup (~10 minutes)

1. **Install QGIS LTR** if you don't already have it: <https://qgis.org/download/> — get the LTR (Long Term Release) build.
2. **Install QFieldSync plugin**: in QGIS → `Plugins → Manage and Install Plugins` → search "QFieldSync" → Install.
3. **Build the project**:
   - Open this folder in QGIS via `File → Open` and pick `chipanga.gpkg`.
   - Open Python Console: `Plugins → Python Console` (or `Ctrl+Alt+P`).
   - Click "Show Editor" → open `setup_chipanga_project.py` → green ▶ Run.
   - Script writes `chipanga.qgz` next to itself.
4. **Pre-cache offline satellite tiles** (so Charlie doesn't need cellular):
   - In QGIS: `Project → Properties → Variables` — note the bbox of your area is roughly lat -6.235 to -6.240, lon 35.344 to 35.347 (school + plots).
   - Run `QField → Package for QField` (from QFieldSync menu).
   - When asked, choose "Convert to MBTiles (Offline)" for the ESRI World Imagery basemap. Set zoom range 14–19 and limit area to ~500m around the school.
5. **Package**: QFieldSync will produce a folder like `chipanga_qfield/`. That's what goes to Charlie.

## Sending to Charlie (file transfer)

Zip the QFieldSync output folder and send via WhatsApp / email / Google Drive link. He extracts and copies it onto his phone (instructions in `README_charlie_field.md`).

## Receiving updates back

When Charlie sends his updated folder back:
1. Extract the zip.
2. In QGIS → `QField → Synchronize from QField` → point at the folder.
3. QFieldSync writes the edited features back into `chipanga.gpkg`. Done — you now have authoritative data.

## Iterating

Want a new layer or new dropdown option? Edit `setup_chipanga_project.py`, re-run it (it clears and rebuilds the project), repackage, send. If you only added options to existing dropdowns, Charlie can keep collecting in the old package — the new options will just be missing on his end.

## Sanity check on the GeoPackage

The 7 feature layers and their geometries:

| Layer | Geometry | EPSG | Pre-filled |
|---|---|---|---|
| school_buildings | Polygon | 4326 | 6 buildings (BLD_001–006) |
| garden_plots | Polygon | 4326 | empty |
| fence_areas | Polygon | 4326 | empty |
| solar_array | Polygon | 4326 | empty |
| water_towers | Point | 4326 | empty |
| infrastructure_points | Point | 4326 | empty |
| water_pipelines | LineString | 4326 | empty |

If Charlie says he can't edit a layer in QField, double-check: he should have opened the `.qgz` file (not the `.gpkg` directly). QField only enables editing on layers from a project file.
