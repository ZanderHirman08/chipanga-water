# Project Recap & Next Steps

_Last updated: 2026-05-08_

## What this project is

Helping Charlie (Peace Corps volunteer in Chipanga, Bahi District, Dodoma Region, Tanzania) document and visualize a community water + gardens project funded by Rotary clubs (~$7,000 total, including a Longmont Rotary grant). Two audiences:

- **On the ground in Chipanga** — schematic map for the village/school to use day-to-day
- **Donors + Peace Corps reporting** — formal report map + interactive online dashboard

Plus a calc model so the water + food numbers behind the project are defensible.

## What's built and ready

### 1. Calc model — `chipanga_water_food_model.xlsx`

Multi-sheet Excel workbook, Dodoma climate calibrated, zero formula errors across 276 formulas. Sheets:

- **Dashboard** — donor-friendly headline numbers
- **Inputs** — every editable assumption, color-coded (blue = input, yellow = key assumption to verify)
- **Well_Solar** — monthly water supply potential factoring solar variation
- **ET_Demand** — crop water demand by month (FAO-56 ET₀ × crop coefficients)
- **Irrigation** — drip vs hand-watering comparison, mulch + compost savings
- **Tank_Sizing** — peak-month stress test, buffer days
- **Food_Yield** — annual production by crop, people-fed estimates
- **Sources** — references for every default

**Headline numbers right now** (drip + mulch + compost, central Tanzania defaults):
- ~10M L/year water supply, 27,300 L/day average
- 6,070 m² productive area (1.5 acres)
- ~58 tonnes/year mixed vegetables
- ~400 people fed year-round at FAO 0.4 kg/person/day

**Two findings worth flagging to Charlie:**
- Tank buffer at peak (Oct) is only ~0.7 days — if pump goes down on a hot dry day, gardens have less than 24 hours of cushion
- Nov-Feb shows small modeled deficit, but those are rainy-season months and the model doesn't credit rainfall yet (intentional dry-season focus)

### 2. Spatial data layer — `master/chipanga_master.gpkg`

Single GeoPackage with 7 layers, all in EPSG:4326 (matches QField), full schemas with stable ID fields and `photo_path` for QField attachments:

| Layer | Geometry | Status |
|---|---|---|
| school_buildings | Polygon | 6 features (Charlie traced from satellite imagery) |
| garden_plots | Polygon | empty — awaiting Charlie's field collection |
| fence_areas | Polygon | empty |
| solar_array | Polygon | empty |
| water_towers | Point | empty |
| infrastructure_points | Point | empty |
| water_pipelines | Line | empty |

### 3. Sync workflow — `scripts/sync_charlie.py`

When Charlie sends back his QField gpkg, one command merges it into the master, regenerates all the web map GeoJSONs, and updates the calc model with measured plot areas. **Tested end-to-end** with 28 fake features across all 7 layers; zero errors, idempotent on re-run.

### 4. Online dashboard — `docs/index.html`

Self-contained HTML/Leaflet single-page app:
- Esri satellite imagery basemap
- All 7 layers with toggle controls
- Click any feature → full attribute popup
- Sidebar with calc-model headline numbers
- Mobile responsive
- Placeholder features rendered with dashed lines + banner so it's obvious what's real vs demo

Deployment guide ready at `GITHUB_SETUP.md` — GitHub Pages, free forever, ~15 min initial setup.

### 5. Print layouts — `scripts/setup_qgis_layouts.py`

Single PyQGIS script generates two print layouts when run inside QGIS Python Console:

- **Village Schematic** (A2 landscape) — bilingual title (Swahili + English), no satellite (cleaner look), bilingual glossary box (Kisima/borehole, Mnara wa Maji/water tower, Bustani/garden, etc.), plot owner labels
- **Formal Report** (A3 landscape) — satellite imagery base, full cartographic furniture (north arrow, scale bar, legend, title block), embedded calc-summary panel

Both idempotent — re-run after any sync to refresh with latest data. See `scripts/LAYOUT_GUIDE.md`.

### 6. QField package for Charlie — `chipanga_qfield_pkg/`

Already deployed to Charlie via WhatsApp. Contains:
- `Charlie.zip` — what he installed on his phone
- `Charlie/` folder — the unpacked QField project
- `Charlie_Field_Guide.pdf` — install + usage instructions
- `WALKTHROUGH.md` — Zander's step-by-step

### 7. Documentation

- `README.md` — project root, file map + workflows
- `PROJECT_RECAP.md` — this doc
- `CHARLIE_INFO_REQUEST.md` — what to ask Charlie for next (one paste-able WhatsApp message at the bottom)
- `scripts/LAYOUT_GUIDE.md` — running the QGIS print layout script
- `GITHUB_SETUP.md` — putting the dashboard online

## Status of each deliverable

| Deliverable | Status | Blocker |
|---|---|---|
| Calc model | ✅ Done & verified | None |
| Master geopackage | ✅ Schemas locked | None — awaiting field data |
| Sync workflow | ✅ Done & tested | None |
| Web map prototype | ✅ Done | None — preview locally now |
| Web map deployed publicly | ⬜ Ready to deploy | 15 min of your time + GitHub account |
| Village schematic map | 🟨 Template ready | Real plot/infrastructure coordinates |
| Charlie's formal report | 🟨 Template ready | Real plot/infrastructure coordinates |
| Charlie's data collection | ⏳ In progress | Charlie at site / on trip |

## Next steps — sequenced

### While Charlie's on his trip (next ~few days)

**Optional quick wins:**

1. **Deploy the web map** — even with placeholder data. Donors can preview the format. Real data fills in when Charlie syncs. Follow `GITHUB_SETUP.md`. ~15 min.
2. **Test the QGIS layouts** — open QGIS, run `scripts/setup_qgis_layouts.py`, see what the village schematic + formal report look like with placeholder data. Helps you spot styling issues now rather than after Charlie's data lands.
3. **Send Charlie the info request** — copy the WhatsApp message at the bottom of `CHARLIE_INFO_REQUEST.md`.

**Nothing blocking** — these are just to have polished outputs ready when his data arrives.

### When Charlie sends data back

1. Save his returned `chipanga.gpkg` somewhere on your machine
2. `python3 scripts/sync_charlie.py /path/to/his.gpkg`
3. Open QGIS → Run `scripts/setup_qgis_layouts.py` → export both layouts to PDF
4. Push updated `docs/data/*.geojson` to your GitHub repo (drag-and-drop in browser)
5. Send Rotary the public URL + the formal report PDF
6. Print + laminate the village schematic PDF, get it to Charlie or the school

### Once project is operational

- **Periodic re-sync** as Charlie measures more (drawdown after a few months, actual yields after a season, photos)
- **Add rainfall data** to the calc model when you have local met data — model the rainy season properly rather than zero-rain assumption
- **Consider a follow-up: cellular flow meter** if the well is at risk of overuse and remote monitoring becomes affordable later (out of scope for now)

## What I'd watch for

- **The 0.7-day buffer at peak** — talk to Charlie about whether it's worth sizing up to a 5,000 L tank for the school or a third 10,000 L for the gardens. Cheaper to build now than later.
- **Pump nameplate vs measured** — the whole model rests on 5,000 L/hr. Worth having Charlie confirm this with a bucket test once it's running.
- **Solar / pump matching** — Dodoma has good sun, but if the panel array can't actually drive a 5,000 L/hr pump for the assumed useful-sun hours, supply numbers shrink. Charlie's panel-wattage data will close this.
- **Crop coefficients are FAO defaults** — local cultivars (especially **sukuma wiki** vs amaranth as the leafy-greens default) may have different water needs. Worth swapping in once Charlie talks to the women's cooperative.

## File organization (post-cleanup)

Old `Chipanga_Water_Project/` folder consolidated into `Tanzania Map/_archive_old_project/`. Tanzania Map is now the single project root. See `README.md` for the file tree.

You'll see an empty `Chipanga_Water_Project/` mount in your Cowork sidebar — safe to remove from your selected folders since everything moved.
