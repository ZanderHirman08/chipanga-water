# Chipanga QField — End-to-End Walkthrough

This is the complete step-by-step from a fresh computer through Charlie having a working data-collection package on his phone. Read top to bottom the first time. Total time: ~45 minutes for Phase 1 + 2, then ~10 minutes for Phase 3 each time you send a new version.

**Files referenced live in:** `/Users/zander/Documents/Claude/Projects/Tanzania Map/chipanga_qfield_pkg/`

---

## Phase 0 — Quick checklist

Before starting, you'll need:
- [ ] A computer (Mac or Windows) with internet
- [ ] About 1 GB free disk space (mostly for satellite tiles)
- [ ] Your phone (Android or iPhone) with at least 200 MB free
- [ ] Charlie's phone model (Android vs iPhone) so you can send the right format

---

## Phase 1 — Computer setup (~20 min)

### 1.1 Install QGIS

1. Go to **<https://qgis.org/download/>**
2. Click your OS (Mac or Windows). Always pick the **LTR (Long Term Release)** version — it's the most stable.
3. Run the installer. On Mac, drag QGIS into your Applications folder.
4. Open QGIS. First launch can take 30–60 seconds. You should land on a blank project view.

### 1.2 Install QFieldSync plugin

1. In QGIS top menu: **Plugins → Manage and Install Plugins…**
2. In the search box, type `QFieldSync`.
3. Click the plugin in the list, then click **Install Plugin**.
4. When you see "Plugin installed successfully," close the dialog.
5. You should now see a new top-menu item or icon called **QField** (sometimes nested under Plugins → QFieldSync).

### 1.3 Run the setup script

1. In QGIS: **Plugins → Python Console** (or press `Ctrl+Alt+P` / `Cmd+Alt+P`).
2. A console panel opens at the bottom. Click the **Show Editor** icon (looks like a small notepad) on the toolbar inside that panel.
3. In the editor that appears, click the **Open Script** icon (folder).
4. Navigate to `Tanzania Map/chipanga_qfield_pkg/` and select `setup_chipanga_project.py`.
5. Click the **green ▶ Run Script** button at the top of the editor.
6. Watch the console output. You should see lines like:
   ```
   Building project from: …/chipanga.gpkg
     + basemap: ESRI World Imagery
     + layer: School Buildings
     + layer: Garden Plots
     …
   Project saved: …/chipanga.qgz  (ok=True)
   ```

   If you get an error about `__file__`, save the script first (`Ctrl+S` / `Cmd+S`) and re-run.

### 1.4 Open the project and sanity-check

1. **File → Open** → select `chipanga.qgz` from the same folder.
2. You should see:
   - Satellite imagery loads (give it a few seconds for tiles)
   - 6 yellow polygons at the school location (the buildings)
   - In the Layers panel on the left: 7 vector layers + 1 raster (ESRI World Imagery)
3. Right-click on **School Buildings** layer → **Open Attribute Table**. You should see 6 rows, BLD_001 through BLD_006.
4. At the **top-left of the attribute table window**, find the two view-mode icons. The default is **table view** (grid/spreadsheet icon). Click the **form view** icon (single rectangular form/card) to switch. Now you'll see one building at a time as a form with all the widgets: `building_use` dropdown, `roof_type` dropdown, `condition` dropdown, photo button, etc. Click each building in the list on the left to confirm the dropdowns work — that's proof the script wired everything up correctly.
5. Switch back to table view if you like, or close the attribute table.

If any of this looks wrong, see the **Troubleshooting** section at the end.

---

## Phase 2 — Test on your own phone (~15 min)

Before sending to Charlie, you should test the whole loop yourself. This catches install issues, GPS problems, and any layer config you'd want to fix.

### 2.1 Install QField on your phone

- **Android**: Play Store → search **"QField"** → publisher should be **OPENGIS.ch** → Install
- **iPhone**: App Store → search **"QField"** → Install

### 2.2 Package the project for QField (with offline tiles)

1. In QGIS, with `chipanga.qgz` open:
2. Click the **QField** menu → **Package for QField**. (If you can't find it, try **Plugins → QFieldSync → Package for QField**.)
3. A dialog opens. Settings:
   - **Export folder**: pick a fresh empty folder. I'd suggest `~/Desktop/chipanga_qfield_test/`.
   - **Action for layers**: leave defaults (Vector layers stay editable).
   - For the **ESRI World Imagery** raster, change the action dropdown to **"Convert to MBTiles (offline)"**.
   - **Map theme** (if asked): leave as default.
4. Click **Create**. This downloads satellite tiles for offline use — takes 1–5 minutes depending on the area and your internet. You'll see progress bars.
5. When done, the export folder will contain `chipanga.qgz`, `chipanga.gpkg`, and an `mbtiles/` subfolder. That whole folder is what goes on the phone.

### 2.3 Copy onto your phone

**Android (USB cable, easiest):**
1. Plug phone into computer.
2. On the phone, swipe down notifications → tap "USB" notification → choose **"File transfer"** mode.
3. On Mac: download and install **"Android File Transfer"** if you don't have it (<https://www.android.com/filetransfer/>).
4. Open the phone in Finder/Explorer/Android File Transfer.
5. Navigate to: `Internal Storage / Android / data / ch.opengis.qfield / files / Imported Projects /`
   - On newer Android (13+), this path may be hidden — if so, copy to `Documents/QField/` instead. Open QField on phone → Settings → "Imported Projects directory" and point at wherever you put it.
6. Drag the entire `chipanga_qfield_test` folder there.
7. Eject the phone.

**iPhone (AirDrop):**
1. On your Mac: Right-click the `chipanga_qfield_test` folder → **Compress** to make a zip.
2. AirDrop the zip to your iPhone (or email it to yourself).
3. On phone: open **Files** app → find the zip → tap to unzip.
4. Long-press the unzipped folder → **Move** → put it inside the **QField** folder if shown, or just leave it in **On My iPhone**.

### 2.4 Open in QField

1. Launch the **QField** app on your phone.
2. On the home screen, you should see a list of available projects. Tap **chipanga**.
3. The map loads. You'll see:
   - Satellite imagery (offline, from your cached MBTiles)
   - 6 school building polygons
   - Layer panel on the right (tap the right-edge tab to expand)

### 2.5 Try collecting a test feature

1. Step outside or somewhere with sky view (GPS doesn't work well indoors).
2. Wait ~10 seconds. The accuracy indicator at the top should drop to single digits (e.g., "±5m").
3. Tap the **pencil icon** at top-right to enter edit mode.
4. In the layer panel, tap **Garden Plots** to make it the active editing layer.
5. Tap the **+** button at the bottom.
6. Tap the **GPS button** (crosshair icon) to add a vertex at your current location. Walk to a different spot and tap GPS again. Repeat for at least 3 points to make a triangle. Then tap the **green check** to finish the geometry.
7. The form opens. Pick a `group_name` from the dropdown. Try the photo field — it should open the camera. Save with another green check.
8. Verify the polygon appears on the map. Tap it to confirm the form data saved.

### 2.6 Sync the test data back to your computer

1. Plug your phone back in (or AirDrop the folder back).
2. Copy the `chipanga_qfield_test` folder from the phone back to your computer (overwriting your original).
3. In QGIS: **QField → Synchronize from QField** → point at the folder.
4. QFieldSync writes your test feature into `chipanga.gpkg`. You should see it in QGIS now.
5. **Delete the test feature** before you send anything to Charlie: open the Garden Plots attribute table, select your test row, hit Delete.

If any step in 2.1–2.6 broke, fix it now before sending to Charlie. He won't have you to troubleshoot in real time.

---

## Phase 3 — Send to Charlie (~10 min)

### 3.1 Make a clean package for Charlie

1. Make sure the test feature from Phase 2 is deleted.
2. In QGIS, with `chipanga.qgz` open: **QField → Package for QField** again.
3. Export folder: `~/Desktop/chipanga_for_charlie/`.
4. Same settings as 2.2 (convert raster to MBTiles).
5. Click **Create** and wait for tiles.

### 3.2 Compress for sending

1. Locate the `chipanga_for_charlie` folder in Finder/Explorer.
2. Right-click → **Compress**. You get `chipanga_for_charlie.zip`.
3. Check the size:
   - Under 100 MB → can send via WhatsApp directly
   - 100 MB to 25 GB → use Google Drive / Dropbox / WeTransfer
   - Over that → reduce the offline tile zoom range and re-package

### 3.3 Choose a delivery channel

| Charlie's situation | Best channel |
|---|---|
| Reliable Wi-Fi | Google Drive link (just send him the URL) |
| Cellular only, decent connection | WhatsApp file send |
| Spotty connection, in country a while | WeTransfer or split-zip + WhatsApp |
| Meeting in person before he leaves | Just put it on a USB drive |

For Google Drive:
1. Upload `chipanga_for_charlie.zip` to Drive
2. Right-click → **Share** → set to **"Anyone with the link can view"**
3. Copy the link, send to Charlie via WhatsApp/SMS

### 3.4 Send Charlie the field guide

Also send him **`README_charlie_field.md`** — that's his step-by-step. He can read it on his phone in any text app, or you can paste the contents into a WhatsApp message.

If you want a prettier version, open it in a markdown viewer and export as PDF.

### 3.5 Optional: a quick priority message to Charlie

Suggested WhatsApp:

> Hey Charlie — sending you the QField package. Here's what to prioritize when you go to site:
>
> 1. Borehole point (most important — get the GPS, depth, and output rate)
> 2. Plot 11 boundary (where the borehole + solar array sit)
> 3. Plot 12 boundary (school garden)
> 4. Women's plots 1–10 perimeters
> 5. Pipe network (mainline, submains, driplines)
> 6. Water towers (school + garden)
> 7. Solar array footprint + panel count
> 8. Fence around the well
>
> Take a phone photo on every feature you can — the donor map needs them. Don't worry about being perfect, I'll clean up on the desktop side.
>
> When you're done, zip the chipanga folder and send it back over WhatsApp. Asante!

---

## Phase 4 — When Charlie sends data back

1. Save the zip he sends → unzip.
2. In QGIS, with `chipanga.qgz` open: **QField → Synchronize from QField** → point at his folder.
3. QFieldSync merges his edits into your master `chipanga.gpkg`.
4. Save the project. You now have authoritative GPS-anchored data.
5. At this point we can resume the schematic + georeferenced maps and the water/food calculations with real numbers.

---

## Troubleshooting

**"Plugin not found" when running setup script**
You don't need any extra plugin to run the script — the imports are core QGIS. If you see `ImportError: qgis.core`, you're running Python 3 in a regular terminal, not the QGIS Python console. The script must be run inside QGIS.

**Script error: `chipanga.gpkg not found`**
The script looks for `chipanga.gpkg` in the same folder as the script. Confirm both files are in `chipanga_qfield_pkg/` and you opened the script from there.

**Satellite basemap shows blank gray tiles**
The ESRI XYZ URL needs internet. After running the script, check that the basemap layer in the Layers panel doesn't have a red exclamation mark. If it does, right-click → **Properties → Information** to confirm the URL. Worst case, manually add a basemap: in QGIS Browser → XYZ Tiles → New Connection → URL `https://server.arcgisonline.com/ArcGIS/rest/services/World_Imagery/MapServer/tile/{z}/{y}/{x}`.

**QField on phone says "no projects found"**
You put the folder in the wrong directory. On Android 13+, paths under `Android/data/` are sandboxed. Use Settings inside QField to point at wherever you actually put the folder.

**QField won't let you edit a layer**
The `chipanga.qgz` project file is what makes layers editable in QField. If you opened the `.gpkg` directly, layers will be read-only. Always open the `.qgz`.

**Tiles don't show offline on the phone**
Re-check that you set "Convert to MBTiles" in the QFieldSync packaging dialog. The exported folder should have an `mbtiles/` subfolder. If it doesn't, repackage.

**Photos aren't saving**
QField needs storage permission. On the phone: Settings → Apps → QField → Permissions → grant Camera and Storage.

**Can't find the QField menu in QGIS**
QFieldSync sometimes installs under **Plugins → QFieldSync** instead of a top-level menu. Look there.

---

## Quick reference

| Action | Where |
|---|---|
| Setup script | QGIS Python Console → Editor → Run |
| Package for phone | QField → Package for QField |
| Sync data back | QField → Synchronize from QField |
| Master data file | `chipanga.gpkg` (don't lose this) |
| Project file | `chipanga.qgz` (regenerate from script if lost) |

If you get stuck anywhere, send me the QGIS error message and which step you were on — I'll diagnose.
