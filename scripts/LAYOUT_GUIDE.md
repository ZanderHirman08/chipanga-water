# QGIS Print Layout Guide — Chipanga Project

This explains how to generate, customize, and export the two project maps:

- **Village Schematic** (A2 landscape, bilingual, no satellite imagery) — for printing/laminating at the school or village.
- **Formal Report** (A3 landscape, satellite base, full cartographic furniture) — for Charlie's Peace Corps + Rotary submission.

Both are produced from the same layered GeoPackage, so they always stay in sync with the latest field data.

---

## One-time setup

1. Make sure QGIS Desktop (3.28 or later) is installed.
2. Open QGIS. **Project → New** (do not open the existing `.qgz` yet — the script will create/save it).
3. **Plugins → Python Console** (Ctrl+Alt+P).
4. Click the **Show Editor** icon in the Python Console.
5. **Open Script** → navigate to `scripts/setup_qgis_layouts.py`.
6. Press **Run Script** (green triangle, or Ctrl+R).

You'll see progress messages in the console. When it finishes:

```
  Built layout: Village Schematic
  Built layout: Formal Report
  Saving project to .../Chipanga_Water_Project.qgz ...
DONE. Open Project → Layouts to see them...
```

The project file is saved at `Chipanga_Water_Project.qgz` in the project root.

## Re-running after Charlie sends new data

Whenever Charlie sends back his updated `chipanga.gpkg`:

1. **Run the sync first:** `python3 scripts/sync_charlie.py path/to/charlies.gpkg`
   This updates `master/chipanga_master.gpkg` and re-exports the web-map GeoJSONs.
2. **In QGIS, re-run** `setup_qgis_layouts.py` from the Python Console.
   It's idempotent — it removes previous versions of the two layouts and rebuilds them with the latest data, with the same styling.

## Opening the layouts

Once the script has run:

- **Project → Layouts → Village Schematic**
- **Project → Layouts → Formal Report**

Each opens in its own QGIS layout window.

## Customizing before export

### Village Schematic
- **Title text** lives in the script (`VILLAGE_TITLE`, `VILLAGE_SUBTITLE`, `VILLAGE_FOOTER`). Edit those constants and re-run.
- **Plot labels** show owner names from the `garden_plots.owner` field. Edit names directly in QGIS by toggling layer editing on `garden_plots`, double-clicking a plot, and editing `owner`.
- **Glossary** (yellow box) is hard-coded in the script — edit the `glossary` HTML string in `build_village_layout()`.
- **Colors:** Each layer's color is set in `LAYER_CONFIG`. To change one, edit the hex code and re-run.

### Formal Report
- **Title text** and **footer**: `REPORT_TITLE`, `REPORT_SUBTITLE`, `REPORT_FOOTER`.
- **Date**: shown as `Date: ____` — fill in inside the layout window before exporting.
- **Calc summary panel**: hard-coded inside `add_calc_summary_panel()`. Update those numbers when the spreadsheet changes (or replace the whole text with HTML pulled from Excel).

## Exporting to PDF

In each layout window: **Layout → Export as PDF…** Choose:

- **Village Schematic:** A2, 300 dpi, "Always export as vectors" off (lets you print/scan cleanly).
- **Formal Report:** A3, 300 dpi, embed fonts on.

For the village schematic, take the PDF to a print shop and ask for **A2 lamination** so it survives outdoor posting at the school.

## Troubleshooting

- **"Could not load Esri imagery"** — your machine has no internet at script-run time. The Village Schematic doesn't need it; the Formal Report will fall back to a white background until you re-run with internet.
- **Labels overlap / look messy** — open the layer in QGIS, right-click → **Properties → Labels** and adjust placement, font size, or buffer.
- **Layouts already exist with different names** — the script removes only `"Village Schematic"` and `"Formal Report"`. If you renamed them, the script won't find them; rename back, or delete manually via **Project → Layout Manager**.
- **Map shows wrong extent** — the script auto-fits to the bounding box of all loaded features × 1.4. If you want a specific area, set extent manually in the layout window: select the map → Item Properties → Extent.

## Multi-page report (future enhancement)

The current Formal Report is a single A3 page. To make a multi-page report (overview, infrastructure detail, plots detail, summary stats), add more pages via **Page Properties → Add Page** and duplicate the map frame zoomed to different extents. Easiest done manually in the layout editor — the script is the foundation.
