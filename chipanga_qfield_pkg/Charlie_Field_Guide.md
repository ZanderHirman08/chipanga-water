# Chipanga Mapping — Field Guide

Hey Charlie — here's everything you need to collect GPS data for the well + gardens project. Should take ~30 minutes the first time you set it up, then 1–2 hours of actual collecting at the site.

---

## What you'll need

- Your phone (Android or iPhone)
- The `chipanga_qfield.zip` file from Zander
- About 200 MB free on your phone
- Be **outside with sky view** when collecting — GPS doesn't work well indoors

---

## Step 1 — Install QField

QField is a free app. Search **QField** by **OPENGIS.ch** in your app store.

- **Android**: Google Play Store
- **iPhone**: App Store

When you open it the first time, it'll ask for permissions. **Allow all of these** — without them you can't collect:

- Location (always or while using the app)
- Camera
- Storage / Photos

---

## Step 2 — Get the project onto your phone

### Android

1. Get `chipanga_qfield.zip` onto your phone (WhatsApp, Drive, email).
2. Open your file manager app, find the zip.
3. Tap to extract (some Android file managers call this "unzip" or "extract here").
4. Move the extracted `chipanga_qfield` folder to: `Internal Storage / Android / data / ch.opengis.qfield / files / Imported Projects /`

If your phone (Android 13+) hides that path, just put the folder somewhere you can find — like Documents — and inside QField go to **Settings → Imported Projects directory** and point it at wherever you put the folder.

5. Open QField. The project should appear on the home screen.

### iPhone

1. Save `chipanga_qfield.zip` to the Files app.
2. Tap the zip to unzip — it'll create a folder.
3. Long-press the unzipped folder → **Move** → put it in **On My iPhone → QField**.
4. Open QField. The project appears on the home screen.

---

## Step 3 — Open the project

Tap **chipanga** on the QField home screen. The map loads with satellite imagery and the school buildings highlighted. First load takes ~30 seconds even when you're offline (it's reading from a local tile cache).

---

## Step 4 — How the QField screen works

When the project is open, you've got:

- **Map** — fills the screen, satellite imagery underneath
- **Top bar** — GPS toggle, accuracy reading (±X meters)
- **Right edge tab** — pull this out to see the layer panel
- **Pencil icon at top-right** — toggles **edit mode** on and off
- **Bottom buttons** — change based on what you're doing

**Important rule**: nothing's editable until you tap the pencil. When the pencil is highlighted/yellow, you're in edit mode.

---

## Step 5 — Adding features (three flavors)

You'll be adding three kinds of features depending on the layer:

- **Points** — single GPS spot (borehole, water tower, valve, pump)
- **Lines** — pipes (mainline, submains, driplines)
- **Polygons** — areas with corners (plots, fence, solar array, school buildings)

### Adding a point (e.g., the borehole)

1. **Stand at the spot** you want to record.
2. **Wait 5–10 seconds** for GPS to lock — top bar should show ±3–5 m or better.
3. Tap the **pencil** to enter edit mode.
4. In the right-edge layer panel, tap the layer this belongs to (e.g., Infrastructure Points).
5. Tap the **+** button at the bottom.
6. Tap the **GPS button** (crosshair icon) to drop a point at your current location.
7. The form pops up — fill in the attributes (see Step 6).
8. Tap the **green check** to save.

### Adding a polygon (plot boundary, fence, solar panels)

1. Stand at one corner of the area.
2. Tap **pencil** → tap the layer (e.g., Garden Plots) → tap **+**.
3. Tap **GPS button** to record the first corner.
4. Walk to the next corner. Tap GPS again. Repeat for all corners.
5. After at least 3 corners, tap the **green check** to close the polygon.
6. Form pops up — fill in attributes.
7. Green check again to save.

**Faster alternative**: tap directly on the satellite map for each corner instead of walking. Less accurate but quicker. Walking gives you GPS-grade corners (~3 m accuracy). Map-tapping is fine when the corner is obvious in the satellite imagery.

### Adding a line (water pipes)

1. Tap **pencil** → Water Pipelines layer → **+**.
2. Walk along the pipe path. Tap GPS at the start. Walk to a bend or junction. Tap GPS again. Continue until you reach the end.
3. Tap the **green check** to finish.
4. Fill in the pipe attributes.

For underground pipes you can't see — trace them on the satellite map (tap-tap-tap) using your knowledge of where they go.

---

## Step 6 — Filling in the form

When the form pops up, you'll see fields with dropdowns or text inputs, plus a **photo field** (tap it, the camera opens, take a picture, save).

**Don't worry if you don't know an answer** — leave the field blank. Zander can ask you later or fill it in himself. The most important things are the **geometry** (the GPS shape) and a **photo**.

What each layer asks for:

**School Buildings** — already has 6 buildings pre-loaded. Tap each one, fix the polygon if it's off (drag corners), then fill in:

- `building_use` (classroom, office, kitchen, latrine, etc.)
- `roof_type` (iron sheet, thatch, tile)
- `condition` (good / fair / poor)
- `num_rooms`
- photo

**Garden Plots** — 12 plots total:

- Plots 1–10 = women's group plots (right side from the original map)
- Plot 11 = where the borehole + solar array sit
- Plot 12 = school garden

Fill in `plot_id` (P01–P12), `owner`, `group_name`, `use_type`, `crops`, photo.

**Fence Areas** — perimeter of any fenced area, especially around the well infrastructure.

**Solar Array** — outline the panel area, plus `panel_count` and `panel_watts`.

**Water Towers** — point at each tower base, plus `tank_count`, `tank_capacity_l`, what it serves.

**Infrastructure Points** — borehole, pump, valves, water meter, fittings — one point per item.

- For the borehole specifically: `feature_type` = borehole, `depth_m` = 180, `max_output_lph` = 5000, `install_year`, photo
- For other items: just `feature_type`, `status`, photo

**Water Pipelines** — mainline + submains + driplines. Pick `pipe_type`, `material` (HDPE / PVC), `diameter_in`.

---

## Step 7 — Save often

**Tap the green check after every single feature.** If your phone dies or QField crashes, anything saved is safe; anything mid-edit is lost.

You can exit edit mode (tap the pencil again, it goes un-highlighted) and come back later. Saved features stay on the map.

---

## Step 8 — Tips

- **GPS lock** — wait 10 seconds after starting. Top bar shows accuracy. Aim for ±5 m or better. Single digits are great.
- **Walk slowly** when tracing perimeters. ~3 seconds at each corner before tapping GPS.
- **Cloudy days are fine for GPS** — but bad for clear photos.
- **Phones lose GPS near dense buildings** — step into the open if accuracy spikes.
- **Don't worry about getting it perfect.** Zander can drag corners on the desktop side. Just get it close.
- **Photos are gold.** Even a quick blurry phone photo of every fitting / tank / pipe section tells the donor story far better than just a polygon. Take more than you think you need.

---

## Step 9 — Priority order

If you only have an hour the first day, do items 1–4. The rest can come on a second visit.

1. **Borehole** — point + depth (180 m) + output (5,000 L/hr) + photo
2. **Plot 11 boundary** — the area with borehole + solar array
3. **Plot 12 boundary** — the school garden
4. **Pipe network** — at minimum the mainline; ideally submains too
5. **Women's plots 1–10** — boundaries
6. **Solar array** — footprint + panel count
7. **Water towers** — both, with capacities
8. **Fence around the well**
9. **School buildings** — verify the 6 pre-loaded polygons match reality

---

## Step 10 — Send the data back to Zander

When you're done (or at the end of each day if you want to be safe):

1. **Close QField cleanly** — back to the home screen, no edit mode active.
2. Open your phone's file manager.
3. Find the **chipanga_qfield** folder (wherever you put it in Step 2).
4. **Compress / zip** the whole folder. (Android: long-press → Compress. iOS: long-press in Files → Compress.)
5. **Send the zip to Zander** via WhatsApp, Drive, or email.

That's it. Anything weird that happens, take a screenshot and send it to him — he'll figure out what's going on.

Asante sana!
