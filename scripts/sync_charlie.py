#!/usr/bin/env python3
"""
sync_charlie.py — drop-in script to merge Charlie's QField-collected features
into the Chipanga master GeoPackage and re-export the web map data.

Usage:
    python3 sync_charlie.py /path/to/charlies_returned_chipanga.gpkg

What it does:
    1. Validates the input gpkg has the expected layer schema
    2. Backs up the current master to master/backups/<timestamp>/
    3. Merges features layer-by-layer (insert new, update existing by ID field)
    4. Re-exports every layer as GeoJSON for the web map
    5. Updates the calc model with measured plot areas if Charlie collected them
    6. Prints a clean diff summary

Run this whenever Charlie sends back his updated chipanga.gpkg.
"""

import argparse
import json
import os
import shutil
import sqlite3
import struct
import sys
from datetime import datetime
from pathlib import Path

# --- Paths (relative to this script's location) ---
SCRIPT_DIR = Path(__file__).resolve().parent
PROJECT_ROOT = SCRIPT_DIR.parent
MASTER_GPKG = PROJECT_ROOT / "master" / "chipanga_master.gpkg"
BACKUP_DIR = PROJECT_ROOT / "master" / "backups"
WEB_DATA_DIR = PROJECT_ROOT / "docs" / "data"   # /docs is GitHub Pages convention
CALC_MODEL = PROJECT_ROOT / "chipanga_water_food_model.xlsx"

# --- Layer config: layer_name -> stable ID field for upsert dedup ---
LAYERS = {
    "school_buildings":      "building_id",
    "garden_plots":          "plot_id",
    "fence_areas":           "fence_id",
    "solar_array":           "array_id",
    "water_towers":          "tower_id",
    "infrastructure_points": "feature_id",
    "water_pipelines":       "pipe_id",
}

# =============================================================
# WKB <-> GeoJSON converter (handles Point, LineString, Polygon)
# =============================================================
def parse_gpkg_geom(blob):
    """Strip GeoPackage geometry header, return raw WKB bytes."""
    if blob is None:
        return None
    flags = blob[3]
    env_type = (flags >> 1) & 0x07
    env_sizes = {0: 0, 1: 32, 2: 48, 3: 48, 4: 64}
    return blob[8 + env_sizes.get(env_type, 0):]

def wkb_to_geojson(wkb):
    """Convert WKB bytes to a GeoJSON geometry dict."""
    if wkb is None or len(wkb) < 5:
        return None
    endian = "<" if wkb[0] == 1 else ">"
    gtype = struct.unpack(f"{endian}I", wkb[1:5])[0]
    pos = 5

    def read_uint():
        nonlocal pos
        v = struct.unpack(f"{endian}I", wkb[pos:pos+4])[0]
        pos += 4
        return v

    def read_point():
        nonlocal pos
        x, y = struct.unpack(f"{endian}dd", wkb[pos:pos+16])
        pos += 16
        return [x, y]

    def read_ring():
        n = read_uint()
        return [read_point() for _ in range(n)]

    if gtype == 1:    # Point
        return {"type": "Point", "coordinates": read_point()}
    if gtype == 2:    # LineString
        n = read_uint()
        return {"type": "LineString", "coordinates": [read_point() for _ in range(n)]}
    if gtype == 3:    # Polygon
        n = read_uint()
        return {"type": "Polygon", "coordinates": [read_ring() for _ in range(n)]}
    if gtype == 6:    # MultiPolygon
        n = read_uint()
        polys = []
        for _ in range(n):
            pos += 5  # skip nested header (byteorder + type)
            nr = read_uint()
            polys.append([read_ring() for _ in range(nr)])
        return {"type": "MultiPolygon", "coordinates": polys}
    raise ValueError(f"Unsupported WKB geometry type: {gtype}")

# =============================================================
# Helpers
# =============================================================
def get_user_layers(conn):
    c = conn.cursor()
    c.execute("SELECT table_name, data_type FROM gpkg_contents WHERE data_type='features'")
    return [r[0] for r in c.fetchall()]

def get_columns(conn, table):
    c = conn.cursor()
    c.execute(f"PRAGMA table_info('{table}')")
    return [r[1] for r in c.fetchall()]

def count_features(conn, table):
    return conn.execute(f"SELECT COUNT(*) FROM '{table}'").fetchone()[0]

# =============================================================
# Main steps
# =============================================================
def validate_input(input_path):
    if not Path(input_path).exists():
        sys.exit(f"ERROR: input file not found: {input_path}")
    if not MASTER_GPKG.exists():
        sys.exit(f"ERROR: master gpkg missing at {MASTER_GPKG}")
    in_conn = sqlite3.connect(input_path)
    in_layers = set(get_user_layers(in_conn))
    in_conn.close()
    expected = set(LAYERS.keys())
    missing = expected - in_layers
    if missing:
        print(f"WARNING: input gpkg is missing layers (will be skipped): {missing}")
    extra = in_layers - expected
    if extra:
        print(f"INFO: input gpkg has unexpected layers (ignored): {extra}")

def backup_master():
    ts = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
    backup_path = BACKUP_DIR / f"chipanga_master_{ts}.gpkg"
    BACKUP_DIR.mkdir(parents=True, exist_ok=True)
    shutil.copy2(MASTER_GPKG, backup_path)
    return backup_path

def merge_features(input_path):
    """Upsert features from input → master, keyed by each layer's ID field."""
    summary = {}
    in_conn = sqlite3.connect(input_path)
    master_conn = sqlite3.connect(MASTER_GPKG)

    in_layers = set(get_user_layers(in_conn))

    for layer, id_field in LAYERS.items():
        if layer not in in_layers:
            summary[layer] = {"new": 0, "updated": 0, "skipped": True}
            continue

        in_cols = get_columns(in_conn, layer)
        master_cols = get_columns(master_conn, layer)
        cols = [c for c in in_cols if c in master_cols and c != "fid"]
        # Use double-quoted identifiers, NOT single quotes (those make string literals).
        col_list = ",".join(f'"{c}"' for c in cols)
        placeholders = ",".join("?" * len(cols))

        rows = in_conn.execute(
            f'SELECT {col_list} FROM "{layer}"'
        ).fetchall()
        new_n, upd_n = 0, 0

        for row in rows:
            row_dict = dict(zip(cols, row))
            ident = row_dict.get(id_field)
            existing_fid = None
            if ident:
                r = master_conn.execute(
                    f'SELECT fid FROM "{layer}" WHERE "{id_field}"=?', (ident,)
                ).fetchone()
                if r:
                    existing_fid = r[0]
            if existing_fid is not None:
                set_clause = ",".join(f'"{c}"=?' for c in cols)
                master_conn.execute(
                    f'UPDATE "{layer}" SET {set_clause} WHERE fid=?',
                    list(row) + [existing_fid],
                )
                upd_n += 1
            else:
                master_conn.execute(
                    f'INSERT INTO "{layer}" ({col_list}) VALUES ({placeholders})', row
                )
                new_n += 1

        summary[layer] = {"new": new_n, "updated": upd_n, "skipped": False}
    master_conn.commit()
    master_conn.close()
    in_conn.close()
    return summary

def rebuild_web_map_html():
    """Rebuild the self-contained web_map/index.html with inlined data."""
    try:
        import build_web_map  # local import — sibling script
        build_web_map.main()
    except Exception as e:
        print(f"  WARN: could not rebuild web_map/index.html: {e}")


def export_geojson():
    """Re-export every master layer as GeoJSON for the web map.
    Features whose stable ID starts with 'DRAFT_' get _is_placeholder=true
    so the web map renders them with dashed lines.
    Also rebuilds the self-contained web_map/index.html."""
    WEB_DATA_DIR.mkdir(parents=True, exist_ok=True)
    conn = sqlite3.connect(MASTER_GPKG)
    counts = {}
    for layer, id_field in LAYERS.items():
        cols = get_columns(conn, layer)
        non_geom = [c for c in cols if c not in ("geom",)]
        col_list = ",".join(f'"{c}"' for c in non_geom)
        rows = conn.execute(f'SELECT {col_list}, geom FROM "{layer}"').fetchall()
        features = []
        any_placeholder = False
        for row in rows:
            props = dict(zip(non_geom, row[:-1]))
            geom_blob = row[-1]
            wkb = parse_gpkg_geom(geom_blob)
            geom = wkb_to_geojson(wkb) if wkb else None
            ident = props.get(id_field) or ""
            is_draft = isinstance(ident, str) and ident.startswith("DRAFT_")
            props["_is_placeholder"] = is_draft
            if is_draft:
                any_placeholder = True
            features.append({
                "type": "Feature",
                "geometry": geom,
                "properties": props,
            })
        fc = {"type": "FeatureCollection", "name": layer,
              "_is_placeholder_layer": any_placeholder,
              "features": features}
        out = WEB_DATA_DIR / f"{layer}.geojson"
        out.write_text(json.dumps(fc, default=str), encoding="utf-8")
        counts[layer] = len(features)
    conn.close()
    rebuild_web_map_html()
    return counts

def update_calc_model_areas():
    """If Charlie collected garden_plots with area_m2 set, update the calc model."""
    if not CALC_MODEL.exists():
        return None
    conn = sqlite3.connect(MASTER_GPKG)
    rows = conn.execute(
        "SELECT plot_id, group_name, area_m2 FROM garden_plots WHERE area_m2 IS NOT NULL"
    ).fetchall()
    conn.close()
    if not rows:
        return None
    womens_total = sum(r[2] for r in rows if (r[1] or "").lower().startswith(("women", "wom")))
    school_total = sum(r[2] for r in rows if (r[1] or "").lower().startswith("school"))
    if womens_total <= 0 and school_total <= 0:
        return None
    try:
        from openpyxl import load_workbook
    except ImportError:
        print("INFO: openpyxl not installed — skipping calc model update")
        return None
    wb = load_workbook(CALC_MODEL)
    inp = wb["Inputs"]
    ACRES_PER_M2 = 1 / 4046.86
    if womens_total > 0:
        inp["B30"] = round(womens_total * ACRES_PER_M2, 4)
        inp["B30"].comment = None
    if school_total > 0:
        inp["B32"] = round(school_total * ACRES_PER_M2, 4)
    wb.save(CALC_MODEL)
    return {"womens_m2": womens_total, "school_m2": school_total}

# =============================================================
# Diff reporter
# =============================================================
def print_summary(backup_path, merge_summary, export_counts, calc_update):
    bar = "=" * 64
    print("\n" + bar)
    print("SYNC COMPLETE")
    print(bar)
    print(f"  Backup:        {backup_path.relative_to(PROJECT_ROOT)}")
    print(f"  Master gpkg:   {MASTER_GPKG.relative_to(PROJECT_ROOT)}")
    print(f"  Web data dir:  {WEB_DATA_DIR.relative_to(PROJECT_ROOT)}")
    print()
    print(f"  {'Layer':<24} {'New':>6} {'Updated':>8} {'Total in master':>16}")
    print(f"  {'-'*24} {'-'*6} {'-'*8} {'-'*16}")
    for layer in LAYERS:
        s = merge_summary.get(layer, {})
        if s.get("skipped"):
            tag = "(skipped)"
            print(f"  {layer:<24} {tag:>6} {'':>8} {export_counts.get(layer, '?'):>16}")
        else:
            print(f"  {layer:<24} {s['new']:>6} {s['updated']:>8} {export_counts.get(layer, '?'):>16}")
    if calc_update:
        print()
        print("  Calc model updated with measured plot areas:")
        print(f"    Women's gardens total: {calc_update['womens_m2']:,.0f} m²")
        print(f"    School garden total:   {calc_update['school_m2']:,.0f} m²")
    print(bar + "\n")

def main():
    p = argparse.ArgumentParser(description="Merge Charlie's gpkg into Chipanga master.")
    p.add_argument("input", help="Path to Charlie's returned chipanga.gpkg")
    p.add_argument("--no-export", action="store_true", help="Skip GeoJSON export step")
    p.add_argument("--no-calc-update", action="store_true",
                   help="Don't update calc model with measured plot areas")
    args = p.parse_args()

    validate_input(args.input)
    backup_path = backup_master()
    merge_summary = merge_features(args.input)
    export_counts = {} if args.no_export else export_geojson()
    if not args.no_export and not export_counts:
        # ensure we still get counts for summary
        conn = sqlite3.connect(MASTER_GPKG)
        export_counts = {l: count_features(conn, l) for l in LAYERS}
        conn.close()
    calc_update = None if args.no_calc_update else update_calc_model_areas()
    print_summary(backup_path, merge_summary, export_counts, calc_update)

if __name__ == "__main__":
    main()
