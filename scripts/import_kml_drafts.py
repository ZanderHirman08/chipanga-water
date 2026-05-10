#!/usr/bin/env python3
"""
import_kml_drafts.py — import Charlie's Google Earth KML as draft features
into the master GeoPackage.

Use case: Charlie sends a rough Google Earth digitization (.kml) as an
intermediate step before he collects real GPS data with QField in the field.
This script imports those rough features as DRAFT_* IDs with a notes flag,
so they're clearly marked as estimates and won't conflict with real QField
data when it arrives.

Idempotent: re-running removes existing DRAFT_* features first, so you can
re-import an updated KML without duplicates.

Usage:
    python3 scripts/import_kml_drafts.py /path/to/file.kml

What it does:
    1. Removes all existing DRAFT_* features from the master gpkg
    2. Parses the KML, classifies each placemark by name → target layer
    3. Inserts new draft features with DRAFT_<n> IDs + a notes flag
    4. Regenerates web_map/data/*.geojson

Mapping (placemark name keyword → master layer):
    "garden"        → garden_plots
    "borehole"      → infrastructure_points (feature_type=borehole)
    "tank","tower"  → water_towers
    "solar"         → solar_array
    "fence"         → fence_areas
    LineString *    → water_pipelines (regardless of name)
"""

import argparse, sqlite3, struct, sys
from datetime import datetime
from pathlib import Path
import xml.etree.ElementTree as ET

SCRIPT_DIR = Path(__file__).resolve().parent
PROJECT_ROOT = SCRIPT_DIR.parent
MASTER_GPKG = PROJECT_ROOT / "master" / "chipanga_master.gpkg"
KML_NS = {"k": "http://www.opengis.net/kml/2.2"}
DRAFT_NOTE = "DRAFT - Google Earth estimate, replace with QField data"

# =============================================================
# WKB writers (write GPKG geometry blob with WGS84 SRS)
# =============================================================
def gpkg_wrap(wkb_bytes, srs_id=4326):
    return b"GP\x00\x01" + struct.pack("<I", srs_id) + wkb_bytes

def wkb_point(x, y):
    return gpkg_wrap(struct.pack("<BIdd", 1, 1, x, y))

def wkb_linestring(coords):
    body = struct.pack("<BII", 1, 2, len(coords))
    for x, y in coords:
        body += struct.pack("<dd", x, y)
    return gpkg_wrap(body)

def wkb_polygon(rings):
    body = struct.pack("<BII", 1, 3, len(rings))
    for ring in rings:
        body += struct.pack("<I", len(ring))
        for x, y in ring:
            body += struct.pack("<dd", x, y)
    return gpkg_wrap(body)

# =============================================================
# KML parsing
# =============================================================
def parse_coords(text):
    """KML coords format: 'lon,lat,alt lon,lat,alt ...' → list of (lon, lat) tuples."""
    pts = []
    for token in text.strip().split():
        parts = token.strip().split(",")
        if len(parts) >= 2:
            pts.append((float(parts[0]), float(parts[1])))
    return pts

def extract_placemarks(kml_path):
    """Return list of dicts: {name, geom_type, coords}."""
    tree = ET.parse(kml_path)
    root = tree.getroot()
    out = []
    for pm in root.iter("{http://www.opengis.net/kml/2.2}Placemark"):
        name_el = pm.find("k:name", KML_NS)
        name = name_el.text.strip() if name_el is not None and name_el.text else "(unnamed)"
        for geom_tag, label in [("Polygon", "polygon"),
                                 ("LineString", "line"),
                                 ("Point", "point")]:
            g = pm.find(f".//k:{geom_tag}", KML_NS)
            if g is None:
                continue
            coords_el = g.find(".//k:coordinates", KML_NS)
            if coords_el is None or not coords_el.text:
                continue
            coords = parse_coords(coords_el.text)
            if not coords:
                continue
            out.append({"name": name, "geom_type": label, "coords": coords})
            break
    return out

# =============================================================
# Classification
# =============================================================
def classify(placemark):
    """Return (layer_name, attribute_dict) based on name + geometry."""
    name = placemark["name"].lower()
    geom = placemark["geom_type"]

    if geom == "line":
        # All lines → pipelines
        return "water_pipelines", {
            "pipe_type": "supply" if "filling" in name or "distribution" in name else "distribution",
            "material": "HDPE",
            "buried": "unknown",
            "notes": f"{placemark['name']} - {DRAFT_NOTE}",
        }

    if "garden" in name:
        is_school = "school" in name
        return "garden_plots", {
            "plot_number": 12 if is_school else 1,
            "owner": "School" if is_school else "Women's cooperative (boundary)",
            "group_name": "School" if is_school else "Women's group",
            "use_type": "vegetable production",
            "area_m2": 3035.0,  # 0.75 acre = 3035 m² per Charlie 2026-05-10
            "crops": "leafy greens, tomato, okra",
            "irrigation_method": "drip (planned)",
            "notes": f"{placemark['name']} - {DRAFT_NOTE}",
        }

    if "borehole" in name or "well" in name:
        return "infrastructure_points", {
            "feature_type": "borehole",
            "depth_m": 180.0,
            "max_output_lph": 5000,
            "diameter_in": 6.0,
            "status": "planned",
            "notes": f"{placemark['name']} - {DRAFT_NOTE}",
        }

    if "tank" in name or "tower" in name:
        is_school = "school" in name
        return "water_towers", {
            "serves": "school" if is_school else "gardens",
            "tank_count": 1 if is_school else 2,
            "tank_capacity_l": 4000 if is_school else 20000,
            "height_m": 4.0,
            "material": "concrete+steel",
            "notes": f"{placemark['name']} - {DRAFT_NOTE}",
        }

    if "solar" in name:
        # Polygon = either the panel array itself or the fenced enclosure.
        # Charlie called it "Solar enclosure" — treat as the solar_array footprint.
        return "solar_array", {
            "panel_count": 12,
            "panel_watts": None,
            "total_watts": None,
            "mounting": "ground-mount",
            "notes": f"{placemark['name']} - {DRAFT_NOTE}",
        }

    if "fence" in name:
        return "fence_areas", {
            "fence_purpose": "infrastructure_security",
            "fence_type": "chain-link",
            "notes": f"{placemark['name']} - {DRAFT_NOTE}",
        }

    return None, None  # unclassified

# =============================================================
# Layer config (ID column for stable upsert)
# =============================================================
LAYERS = {
    "garden_plots":          ("plot_id",    "DRAFT_PLT"),
    "fence_areas":           ("fence_id",   "DRAFT_FNC"),
    "solar_array":           ("array_id",   "DRAFT_SOLAR"),
    "water_towers":          ("tower_id",   "DRAFT_TWR"),
    "infrastructure_points": ("feature_id", "DRAFT_INF"),
    "water_pipelines":       ("pipe_id",    "DRAFT_PIPE"),
}

# =============================================================
# Main
# =============================================================
def remove_existing_drafts(conn):
    """Wipe all DRAFT_* features so re-import is idempotent."""
    counts = {}
    for layer, (id_field, _) in LAYERS.items():
        cur = conn.execute(
            f'DELETE FROM "{layer}" WHERE "{id_field}" LIKE ?', ("DRAFT_%",)
        )
        counts[layer] = cur.rowcount
    return counts

def insert_feature(conn, layer, ident, attrs, geom_blob):
    cols = ["geom"] + list(attrs.keys()) + [LAYERS[layer][0]]
    vals = [geom_blob] + list(attrs.values()) + [ident]
    placeholders = ",".join("?" * len(cols))
    col_list = ",".join(f'"{c}"' for c in cols)
    conn.execute(f'INSERT INTO "{layer}" ({col_list}) VALUES ({placeholders})', vals)

def make_geometry(pm):
    if pm["geom_type"] == "point":
        x, y = pm["coords"][0]
        return wkb_point(x, y)
    if pm["geom_type"] == "line":
        return wkb_linestring(pm["coords"])
    if pm["geom_type"] == "polygon":
        return wkb_polygon([pm["coords"]])
    return None

def import_kml(kml_path, master_path):
    placemarks = extract_placemarks(kml_path)
    print(f"Parsed {len(placemarks)} placemarks from KML")

    conn = sqlite3.connect(master_path)
    deleted = remove_existing_drafts(conn)
    if any(deleted.values()):
        print("Removed existing DRAFT_ features:")
        for layer, n in deleted.items():
            if n:
                print(f"  {layer}: {n}")

    seen_geoms = set()
    counters = {layer: 1 for layer in LAYERS}
    inserted = {layer: 0 for layer in LAYERS}
    skipped = []

    for pm in placemarks:
        # Dedupe identical-coordinate placemarks (Charlie's KML has a dup School Garden)
        key = (pm["name"], tuple(pm["coords"]))
        if key in seen_geoms:
            skipped.append(f"{pm['name']} (duplicate of earlier placemark)")
            continue
        seen_geoms.add(key)

        layer, attrs = classify(pm)
        if layer is None:
            skipped.append(f"{pm['name']} (no matching layer)")
            continue

        prefix = LAYERS[layer][1]
        n = counters[layer]
        ident = f"{prefix}_{n:03d}"
        counters[layer] += 1

        geom_blob = make_geometry(pm)
        if geom_blob is None:
            skipped.append(f"{pm['name']} (could not build geometry)")
            continue

        insert_feature(conn, layer, ident, attrs, geom_blob)
        inserted[layer] += 1

    conn.commit()
    conn.close()

    bar = "=" * 56
    print()
    print(bar)
    print("KML IMPORT COMPLETE")
    print(bar)
    for layer, n in inserted.items():
        if n > 0:
            print(f"  {layer:<22} +{n} draft features")
    if skipped:
        print()
        for s in skipped:
            print(f"  skipped: {s}")
    print(bar)
    return inserted

def main():
    p = argparse.ArgumentParser()
    p.add_argument("kml", help="Path to KML file from Google Earth")
    p.add_argument("--no-export", action="store_true",
                   help="Skip GeoJSON re-export step")
    args = p.parse_args()

    if not Path(args.kml).exists():
        sys.exit(f"ERROR: KML file not found: {args.kml}")
    if not MASTER_GPKG.exists():
        sys.exit(f"ERROR: master gpkg not found: {MASTER_GPKG}")

    import_kml(args.kml, MASTER_GPKG)

    if not args.no_export:
        print("\nRe-exporting GeoJSONs for web map...")
        # Reuse the export step from sync_charlie.py
        sys.path.insert(0, str(SCRIPT_DIR))
        from sync_charlie import export_geojson
        counts = export_geojson()
        for layer, n in counts.items():
            print(f"  {layer:<22} {n} features")

if __name__ == "__main__":
    main()
