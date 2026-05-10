#!/usr/bin/env python3
"""
build_web_map.py — generate a self-contained web_map/index.html with all
GeoJSON data inlined, so it works when opened directly via file:// (no
local web server needed) AND when deployed to GitHub Pages.

Reads:
    web_map/data/*.geojson   (the per-layer geojson exports)

Writes:
    web_map/index.html       (self-contained HTML with embedded data)

Run automatically by sync_charlie.py after every export.
Can also be run standalone:
    python3 scripts/build_web_map.py
"""

import json
from pathlib import Path

SCRIPT_DIR = Path(__file__).resolve().parent
PROJECT_ROOT = SCRIPT_DIR.parent
WEB_MAP_DIR = PROJECT_ROOT / "docs"   # /docs is GitHub Pages convention
DATA_DIR = WEB_MAP_DIR / "data"
OUT_HTML = WEB_MAP_DIR / "index.html"

LAYERS = [
    # (key, label, hex_color, geom)
    ("school_buildings",      "School buildings",      "#c1666b", "polygon"),
    ("garden_plots",          "Garden plots",          "#2e8b57", "polygon"),
    ("fence_areas",           "Fence (security)",      "#888888", "polygon"),
    ("solar_array",           "Solar array",           "#f1a208", "polygon"),
    ("water_towers",          "Water towers + tanks",  "#1f4e78", "point"),
    ("infrastructure_points", "Borehole + taps",       "#0077b6", "point"),
    ("water_pipelines",       "Water pipelines",       "#0096c7", "line"),
]


def load_data():
    """Read every GeoJSON file in data/ — return {key: geojson_dict}."""
    out = {}
    for key, *_ in LAYERS:
        p = DATA_DIR / f"{key}.geojson"
        if p.exists():
            out[key] = json.loads(p.read_text(encoding="utf-8"))
        else:
            out[key] = {"type": "FeatureCollection", "features": [],
                        "_is_placeholder_layer": False}
    return out


def build_html(data):
    layers_js = json.dumps(LAYERS)
    data_js = json.dumps(data, separators=(",", ":"))
    return f"""<!doctype html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>Chipanga Water + Gardens — Project Map</title>
<link rel="stylesheet" href="https://unpkg.com/leaflet@1.9.4/dist/leaflet.css"
      integrity="sha256-p4NxAoJBhIIN+hmNHrzRCf9tD/miZyoHS5obTRR9BMY=" crossorigin="">
<style>
  :root {{
    --bg: #f7f8fa;
    --panel: #ffffff;
    --ink: #1a2332;
    --muted: #6c757d;
    --accent: #1f4e78;
    --accent-soft: #d9e1f2;
    --good: #2e8b57;
    --warn: #c97c00;
    --placeholder: #b39ddb;
  }}
  html, body {{ margin: 0; padding: 0; height: 100%; font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Arial, sans-serif; color: var(--ink); }}
  #app {{ display: flex; height: 100vh; }}
  #map {{ flex: 1; background: #cdd5dc; }}
  #sidebar {{
    width: 360px; background: var(--panel); border-left: 1px solid #e1e4e8;
    overflow-y: auto; padding: 0; box-shadow: -2px 0 8px rgba(0,0,0,0.04);
  }}
  .header {{ background: var(--accent); color: white; padding: 16px 20px; }}
  .header h1 {{ margin: 0; font-size: 18px; font-weight: 600; }}
  .header .sub {{ font-size: 12px; opacity: 0.85; margin-top: 2px; }}
  .section {{ padding: 14px 20px; border-bottom: 1px solid #eef0f2; }}
  .section h2 {{ margin: 0 0 10px 0; font-size: 13px; text-transform: uppercase; letter-spacing: 0.5px; color: var(--muted); font-weight: 600; }}
  .stat-grid {{ display: grid; grid-template-columns: 1fr 1fr; gap: 8px; }}
  .stat {{ background: var(--accent-soft); padding: 10px 12px; border-radius: 6px; }}
  .stat .label {{ font-size: 11px; color: var(--muted); text-transform: uppercase; letter-spacing: 0.3px; }}
  .stat .value {{ font-size: 20px; font-weight: 600; color: var(--accent); margin-top: 2px; line-height: 1.1; }}
  .stat .unit {{ font-size: 11px; color: var(--muted); margin-left: 2px; }}
  .layer-row {{ display: flex; align-items: center; padding: 6px 0; cursor: pointer; user-select: none; }}
  .layer-row:hover {{ background: #f0f4f8; }}
  .layer-row input {{ margin-right: 10px; }}
  .layer-swatch {{ width: 14px; height: 14px; border-radius: 3px; margin-right: 8px; border: 1px solid rgba(0,0,0,0.1); }}
  .layer-row .name {{ flex: 1; font-size: 13px; }}
  .layer-row .count {{ font-size: 11px; color: var(--muted); }}
  .pill {{ display: inline-block; font-size: 10px; padding: 1px 6px; border-radius: 8px; background: var(--placeholder); color: white; margin-left: 6px; text-transform: uppercase; letter-spacing: 0.3px; font-weight: 600; }}
  .banner {{ background: #fff3cd; color: #664d03; padding: 8px 12px; font-size: 12px; border-bottom: 1px solid #ffec99; }}
  .legend-note {{ font-size: 11px; color: var(--muted); margin-top: 6px; }}
  .leaflet-popup-content {{ font-family: inherit; font-size: 13px; }}
  .leaflet-popup-content h3 {{ margin: 0 0 4px 0; font-size: 14px; }}
  .leaflet-popup-content table {{ border-collapse: collapse; margin-top: 4px; font-size: 12px; }}
  .leaflet-popup-content td {{ padding: 1px 6px 1px 0; vertical-align: top; }}
  .leaflet-popup-content td:first-child {{ color: var(--muted); white-space: nowrap; }}
  @media (max-width: 720px) {{
    #app {{ flex-direction: column; }}
    #sidebar {{ width: 100%; height: 50vh; }}
  }}
</style>
</head>
<body>
<div id="app">
  <div id="map"></div>
  <aside id="sidebar">
    <div class="header">
      <h1>Chipanga Water + Gardens</h1>
      <div class="sub">Bahi District, Dodoma Region · Tanzania</div>
    </div>
    <div id="placeholder-banner" class="banner" style="display:none">
      Some layers below show <strong>placeholder data</strong> (dashed lines, lighter colors). They'll be replaced with real measurements when Charlie's QField data syncs.
    </div>
    <div class="section">
      <h2>Project at a glance</h2>
      <div class="stat-grid">
        <div class="stat"><div class="label">Annual water</div><div class="value">10M<span class="unit"> L</span></div></div>
        <div class="stat"><div class="label">Daily supply</div><div class="value">27,300<span class="unit"> L</span></div></div>
        <div class="stat"><div class="label">Productive area</div><div class="value">6,070<span class="unit"> m²</span></div></div>
        <div class="stat"><div class="label">Storage</div><div class="value">24,000<span class="unit"> L</span></div></div>
        <div class="stat"><div class="label">Food output</div><div class="value">~60<span class="unit"> tons/yr</span></div></div>
        <div class="stat"><div class="label">People fed</div><div class="value">~410<span class="unit"> /yr</span></div></div>
      </div>
      <div class="legend-note">From the calc model. Edit the spreadsheet → re-publish to update.</div>
    </div>
    <div class="section">
      <h2>Layers</h2>
      <div id="layer-list"></div>
    </div>
    <div class="section">
      <h2>Funding</h2>
      <div style="font-size: 13px; line-height: 1.5;">
        ~$7,000 raised through Rotary clubs (community + international level, including Longmont Rotary grant). Project supports ~13,440 ward residents through a school + women's-cooperative garden system.
      </div>
    </div>
    <div class="section" style="font-size: 11px; color: var(--muted);">
      Last data sync: <span id="last-sync">checking…</span><br>
      Hosted via GitHub Pages · Built for Charlie's Peace Corps service
    </div>
  </aside>
</div>

<!-- All GeoJSON data inlined so this file works when opened via file:// -->
<script type="application/json" id="layer-data">{data_js}</script>
<script type="application/json" id="layer-config">{layers_js}</script>

<script src="https://unpkg.com/leaflet@1.9.4/dist/leaflet.js"
        integrity="sha256-20nQCchB9co0qIjJZRGuk2/Z9VM+kNiyxNV1lvTlZBo=" crossorigin=""></script>
<script>
const LAYERS = JSON.parse(document.getElementById("layer-config").textContent)
  .map(([key, label, color, geom]) => ({{ key, label, color, geom }}));
const DATA = JSON.parse(document.getElementById("layer-data").textContent);

// --- Map ---
const map = L.map("map", {{ zoomControl: true, minZoom: 3, maxZoom: 20 }})
  .setView([-6.236, 35.346], 18);

// --- Basemaps ---
// Esri World Imagery — reliable, native z19. Allow upscale to z20 for one extra step.
const satEsri = L.tileLayer(
  "https://server.arcgisonline.com/ArcGIS/rest/services/World_Imagery/MapServer/tile/{{z}}/{{y}}/{{x}}",
  {{ attribution: "Imagery © Esri, Maxar, Earthstar Geographics",
     maxZoom: 20, maxNativeZoom: 19 }}
);
// CartoDB Voyager — clean street/road context. Correct OSM-style {{z}}/{{x}}/{{y}} URL.
const streets = L.tileLayer(
  "https://{{s}}.basemaps.cartocdn.com/rastertiles/voyager/{{z}}/{{x}}/{{y}}{{r}}.png",
  {{ attribution: "© OpenStreetMap contributors © CARTO",
     subdomains: "abcd", maxZoom: 20 }}
);
// OpenTopoMap — useful for terrain context around Chipanga.
const terrain = L.tileLayer(
  "https://{{s}}.tile.opentopomap.org/{{z}}/{{x}}/{{y}}.png",
  {{ attribution: "Map data © OpenStreetMap, SRTM | © OpenTopoMap (CC-BY-SA)",
     subdomains: "abc", maxZoom: 17 }}
);
satEsri.addTo(map);
L.control.layers({{
  "Satellite imagery": satEsri,
  "Street map": streets,
  "Terrain": terrain,
}}, null, {{ position: "topleft", collapsed: false }}).addTo(map);

// --- Layers ---
const layerGroups = {{}};
const featureCounts = {{}};
let anyPlaceholder = false;

function makeStyle(cfg, isPlaceholder) {{
  return {{
    color: cfg.color,
    weight: cfg.geom === "line" ? 3 : 2,
    fillColor: cfg.color,
    fillOpacity: cfg.geom === "polygon" ? (cfg.key === "fence_areas" ? 0.05 : 0.30) : 0,
    opacity: 0.95,
    dashArray: isPlaceholder ? "6,4" : null,
  }};
}}

function popupHtml(layerLabel, props) {{
  const skip = new Set(["fid", "_is_placeholder", "photo_path"]);
  const rows = Object.entries(props)
    .filter(([k, v]) => !skip.has(k) && v !== null && v !== "" && v !== undefined)
    .map(([k, v]) => `<tr><td>${{k.replace(/_/g, " ")}}</td><td>${{v}}</td></tr>`)
    .join("");
  const tag = props._is_placeholder ? `<span class="pill">draft</span>` : "";
  return `<h3>${{layerLabel}} ${{tag}}</h3><table>${{rows}}</table>`;
}}

function pointMarker(cfg, latlng, isPlaceholder) {{
  return L.circleMarker(latlng, {{
    radius: 8,
    color: cfg.color,
    weight: 2,
    fillColor: cfg.color,
    fillOpacity: 0.85,
    dashArray: isPlaceholder ? "3,3" : null,
  }});
}}

function loadLayer(cfg) {{
  const gj = DATA[cfg.key] || {{ features: [] }};
  const layer = L.geoJSON(gj, {{
    style: f => makeStyle(cfg, f.properties._is_placeholder),
    pointToLayer: (f, latlng) => pointMarker(cfg, latlng, f.properties._is_placeholder),
    onEachFeature: (f, l) => l.bindPopup(popupHtml(cfg.label, f.properties)),
  }});
  layerGroups[cfg.key] = layer;
  featureCounts[cfg.key] = gj.features.length;
  if (gj._is_placeholder_layer) anyPlaceholder = true;
  if (gj.features.length > 0) layer.addTo(map);
}}

function buildLayerToggle() {{
  const list = document.getElementById("layer-list");
  list.innerHTML = "";
  LAYERS.forEach(cfg => {{
    const row = document.createElement("label");
    row.className = "layer-row";
    const cb = document.createElement("input");
    cb.type = "checkbox";
    cb.checked = featureCounts[cfg.key] > 0;
    cb.disabled = featureCounts[cfg.key] === 0;
    cb.onchange = () => {{
      const grp = layerGroups[cfg.key];
      if (!grp) return;
      cb.checked ? grp.addTo(map) : grp.removeFrom(map);
    }};
    const sw = document.createElement("span");
    sw.className = "layer-swatch";
    sw.style.background = cfg.color;
    if (cfg.geom === "line") {{
      sw.style.background = "transparent";
      sw.style.border = `2px solid ${{cfg.color}}`;
      sw.style.height = "0px";
      sw.style.marginTop = "6px";
    }}
    const name = document.createElement("span");
    name.className = "name";
    name.textContent = cfg.label;
    if (featureCounts[cfg.key] === 0) name.style.opacity = 0.4;
    const count = document.createElement("span");
    count.className = "count";
    count.textContent = featureCounts[cfg.key];
    row.appendChild(cb);
    row.appendChild(sw);
    row.appendChild(name);
    row.appendChild(count);
    list.appendChild(row);
  }});
  if (anyPlaceholder) document.getElementById("placeholder-banner").style.display = "block";
}}

function fitToData() {{
  const bounds = L.latLngBounds([]);
  Object.values(layerGroups).forEach(g => {{
    try {{
      const b = g.getBounds();
      if (b.isValid()) bounds.extend(b);
    }} catch(e) {{}}
  }});
  if (bounds.isValid()) {{
    map.fitBounds(bounds, {{ padding: [50, 50], maxZoom: 18 }});
    // Restrict panning to a 5x area around the data so user can't get lost
    const padded = bounds.pad(2.0);
    map.setMaxBounds(padded);
  }}
}}

// Init
LAYERS.forEach(loadLayer);
buildLayerToggle();
fitToData();
document.getElementById("last-sync").textContent = new Date().toLocaleDateString();
</script>
</body>
</html>
"""


def main():
    if not DATA_DIR.exists():
        raise SystemExit(f"ERROR: data dir not found: {DATA_DIR}")
    data = load_data()
    OUT_HTML.write_text(build_html(data), encoding="utf-8")
    n_features = sum(len(v.get("features", [])) for v in data.values())
    print(f"  Built {OUT_HTML.relative_to(PROJECT_ROOT)}  ({n_features} features inlined)")


if __name__ == "__main__":
    main()
