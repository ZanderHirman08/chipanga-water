# Chipanga Mapping — Field Guide (Charlie)

Hi Charlie! Zander here. This is a quick guide to collecting GPS data for the well + gardens project. Should take you about 30–60 minutes total in the field.

## What you'll need

- Android or iPhone with QField installed (free)
- The `chipanga_qfield` folder from Zander (copy onto your phone)
- Your phone's GPS (no cellular needed once the project is on the phone)

## Step 1 — Install QField

- **Android**: Play Store → search "QField" by OPENGIS.ch → Install.
- **iPhone**: App Store → "QField" → Install.

## Step 2 — Copy the project to your phone

**Android**:
1. Plug phone into computer (or use a file-share app).
2. Copy `chipanga_qfield` folder into: `Internal Storage / Android / data / ch.opengis.qfield / files / Imported Projects /`
3. Open QField. The project will appear on the home screen — tap to open `chipanga.qgz`.

**iPhone**:
1. AirDrop or save the zipped folder to Files app.
2. Unzip in Files.
3. Open QField → tap the folder icon → "Import dataset / project" → select the unzipped folder → open `chipanga.qgz`.

## Step 3 — Collect features

Once the project is open you'll see the satellite map of the school. On the right side is the layer list. Each layer is what you collect:

| Layer | What to collect | Geometry |
|---|---|---|
| **School Buildings** | Already filled in (6 buildings). Tap each one → verify the location → fix the polygon if it's off. Fill in `building_use`, `roof_type`, `condition`, optional photo. | Polygon |
| **Garden Plots** | Walk the corners of each plot. Plot 1–10 = women's plots, Plot 11 = where the borehole / solar array sit, Plot 12 = school garden. | Polygon |
| **Fence Areas** | Walk the perimeter of any fenced area (especially around the well). | Polygon |
| **Solar Array** | Walk the corners of the panel area. Fill in panel count + wattage. | Polygon |
| **Water Towers** | Stand at each tower base, drop a point. Fill in what it serves + tank capacity. | Point |
| **Infrastructure Points** | Borehole (pick `feature_type = borehole`), pump, valves, meters, fittings — drop a point at each. | Point |
| **Water Pipelines** | Walk the line of each pipe. Pick `pipe_type` (mainline / submain / dripline). | Line |

## How to add a feature in QField

1. Tap the **pencil icon** at top-right to enter edit mode.
2. Tap the layer in the legend you want to add to (e.g., "Garden Plots").
3. Tap the **+** button at the bottom.
4. For points: stand at the spot, tap the GPS button to capture your current location, save.
5. For lines: walk the path, the app records as you walk; or tap-tap-tap along the satellite map.
6. For polygons: walk the perimeter (or tap each corner on the map), close the shape, save.
7. The form pops up — fill in what you can, leave blank what you don't know. **Take a photo on the photo field if you want** — taps the camera right inside QField.
8. Tap the **green check** to save.

## Tips

- **GPS lock**: wait ~10 seconds after starting the app for GPS to lock to ~3m accuracy. The accuracy reading is at the top of the screen.
- **Walk slowly** when tracing perimeters. Phone GPS is roughly ±3m.
- **Don't worry about getting it perfect** — you can drag corners later, and Zander will clean things up on the desktop side.
- **Save often**: hit the green check after each feature so nothing's lost.
- **Photos help a lot** — a quick phone photo of each fitting/tank/pipe tells the donor story way better than a polygon alone.

## Step 4 — Send back to Zander

When you're done (or end of each day):
1. Close QField cleanly.
2. Find the `chipanga_qfield` folder on your phone (same path you copied it to).
3. Zip it up (use a free zip app on Android, or "Compress" in iOS Files).
4. Send to Zander via WhatsApp / email / Google Drive — whatever works.

That's it. Asante sana!
