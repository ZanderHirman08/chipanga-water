"""
setup_qgis_layouts.py
=====================
Run this INSIDE QGIS (Plugins → Python Console → Show Editor → Open Script).

What it does:
  1. Loads all 7 layers from master/chipanga_master.gpkg into the current project
  2. Applies clean, donor-quality symbology to each layer
  3. Creates two print layouts:
        - "Village Schematic"  — A2 landscape, bilingual labels (English + Swahili),
          no satellite base, big bold colors, plot owner names visible
        - "Formal Report"      — A3 landscape, satellite imagery base, full
          cartographic furniture (north arrow, scale bar, legend, title block),
          calc-model summary panel
  4. Saves the project as Chipanga_Water_Project.qgz

Re-run any time you add/change layers — it's idempotent (existing layouts get replaced).

Customise the LAYOUT_TITLE / SUBTITLE / FOOTER constants below before running.
"""

import os
from qgis.core import (
    QgsProject, QgsVectorLayer, QgsRasterLayer, QgsLayoutItemMap,
    QgsLayoutItemLabel, QgsLayoutItemLegend, QgsLayoutItemScaleBar,
    QgsLayoutItemPicture, QgsLayoutItemShape, QgsLayoutSize,
    QgsLayoutPoint, QgsUnitTypes, QgsPrintLayout, QgsRectangle,
    QgsCoordinateReferenceSystem, QgsLayerTree, QgsLayerTreeGroup,
    QgsSymbol, QgsSimpleFillSymbolLayer, QgsSimpleLineSymbolLayer,
    QgsSimpleMarkerSymbolLayer, QgsSingleSymbolRenderer,
    QgsCategorizedSymbolRenderer, QgsRendererCategory,
    QgsPalLayerSettings, QgsTextFormat, QgsVectorLayerSimpleLabeling,
    QgsLayoutItemPolyline, QgsLayoutItemPolygon, QgsFillSymbol,
    QgsLineSymbol, QgsMarkerSymbol, QgsLayoutFrame, QgsLayoutItem,
)
from qgis.PyQt.QtCore import Qt, QPointF, QRectF
from qgis.PyQt.QtGui import QColor, QFont, QPolygonF

# =============================================================
# CONFIG — edit these
# =============================================================
PROJECT_DIR = "/Users/zander/Documents/Claude/Projects/Tanzania Map"
GPKG_PATH = os.path.join(PROJECT_DIR, "master", "chipanga_master.gpkg")
PROJECT_FILE = os.path.join(PROJECT_DIR, "Chipanga_Water_Project.qgz")

VILLAGE_TITLE = "Mradi wa Maji na Bustani"
VILLAGE_SUBTITLE = "Water + Garden Project · Chipanga Village"
VILLAGE_FOOTER = "Imefadhiliwa na Rotary + Peace Corps · Funded by Rotary + Peace Corps"

REPORT_TITLE = "Chipanga Water + Garden Project"
REPORT_SUBTITLE = "Bahi District, Dodoma Region, Tanzania · Final Report"
REPORT_FOOTER = "Prepared by Charlie [Last Name] · Peace Corps Tanzania · Funded by Rotary International ($7,000)"

PROJECT_CRS = "EPSG:32736"   # UTM 36S — Bahi District

# =============================================================
# LAYER STYLING
# =============================================================
LAYER_CONFIG = [
    # (layer_name, label, hex_color, geometry_type, label_field, opacity)
    ("school_buildings",      "School Buildings (Majengo ya Shule)",
        "#c1666b", "polygon", "building_name", 0.85),
    ("garden_plots",          "Garden Plots (Mashamba)",
        "#2e8b57", "polygon", "owner",         0.55),
    ("fence_areas",           "Fence (Uzio)",
        "#888888", "polygon", None,            0.10),
    ("solar_array",           "Solar Panels (Paneli za Jua)",
        "#f1a208", "polygon", None,            0.85),
    ("water_towers",          "Water Towers + Tanks (Mnara wa Maji)",
        "#1f4e78", "point",   "serves",        1.0),
    ("infrastructure_points", "Borehole + Taps (Kisima na Mabomba)",
        "#0077b6", "point",   "feature_type",  1.0),
    ("water_pipelines",       "Water Pipelines (Bomba za Maji)",
        "#0096c7", "line",    None,            1.0),
]


def hex_to_qcolor(hex_str, alpha=255):
    c = QColor(hex_str)
    c.setAlpha(alpha)
    return c


def make_polygon_symbol(color_hex, opacity=0.5, outline_width=0.4):
    sym = QgsFillSymbol.createSimple({})
    fill = QgsSimpleFillSymbolLayer()
    fill.setColor(hex_to_qcolor(color_hex, int(opacity * 255)))
    fill.setStrokeColor(hex_to_qcolor(color_hex, 255).darker(140))
    fill.setStrokeWidth(outline_width)
    sym.changeSymbolLayer(0, fill)
    return sym


def make_line_symbol(color_hex, width=0.8):
    sym = QgsLineSymbol.createSimple({})
    line = QgsSimpleLineSymbolLayer()
    line.setColor(hex_to_qcolor(color_hex))
    line.setWidth(width)
    sym.changeSymbolLayer(0, line)
    return sym


def make_point_symbol(color_hex, size=4.0, shape="circle"):
    sym = QgsMarkerSymbol.createSimple({})
    mk = QgsSimpleMarkerSymbolLayer()
    mk.setColor(hex_to_qcolor(color_hex))
    mk.setStrokeColor(QColor("white"))
    mk.setStrokeWidth(0.6)
    mk.setSize(size)
    sym.changeSymbolLayer(0, mk)
    return sym


def style_layer(layer, color_hex, geom_type, opacity, label_field):
    if geom_type == "polygon":
        sym = make_polygon_symbol(color_hex, opacity=opacity)
    elif geom_type == "line":
        sym = make_line_symbol(color_hex, width=1.2)
    else:
        sym = make_point_symbol(color_hex, size=5.0)
    layer.setRenderer(QgsSingleSymbolRenderer(sym))

    # Labels
    if label_field and label_field in [f.name() for f in layer.fields()]:
        text = QgsTextFormat()
        f = QFont("Arial", 8)
        f.setBold(True)
        text.setFont(f)
        text.setColor(QColor("#222"))
        text.buffer().setEnabled(True)
        text.buffer().setSize(0.8)
        text.buffer().setColor(QColor("white"))
        pal = QgsPalLayerSettings()
        pal.fieldName = label_field
        pal.enabled = True
        pal.placement = QgsPalLayerSettings.OverPoint if geom_type == "point" else QgsPalLayerSettings.OverPoint
        pal.setFormat(text)
        layer.setLabelsEnabled(True)
        layer.setLabeling(QgsVectorLayerSimpleLabeling(pal))


# =============================================================
# LOAD LAYERS
# =============================================================
def load_layers(project):
    layers = {}
    for cfg in LAYER_CONFIG:
        name, display, color, geom, label, opacity = cfg
        uri = f"{GPKG_PATH}|layername={name}"
        layer = QgsVectorLayer(uri, display, "ogr")
        if not layer.isValid():
            print(f"  WARN: could not load {name}")
            continue
        style_layer(layer, color, geom, opacity, label)
        project.addMapLayer(layer)
        layers[name] = layer
        print(f"  Loaded: {name}  ({layer.featureCount()} features)")
    return layers


# =============================================================
# BASEMAP — Esri World Imagery for the formal report
# =============================================================
def add_satellite_basemap(project):
    name = "Esri World Imagery"
    existing = [l for l in project.mapLayers().values() if l.name() == name]
    if existing:
        return existing[0]
    url = ("type=xyz&url=https://server.arcgisonline.com/ArcGIS/rest/services/"
           "World_Imagery/MapServer/tile/%7Bz%7D/%7By%7D/%7Bx%7D&zmax=22&zmin=0")
    layer = QgsRasterLayer(url, name, "wms")
    if layer.isValid():
        project.addMapLayer(layer)
        return layer
    print("  WARN: could not load Esri imagery")
    return None


# =============================================================
# LAYOUT BUILDERS
# =============================================================
def remove_existing_layout(project, name):
    mgr = project.layoutManager()
    for layout in mgr.printLayouts():
        if layout.name() == name:
            mgr.removeLayout(layout)
            return


def compute_extent(layers):
    extent = None
    for layer in layers.values():
        e = layer.extent()
        if e.isEmpty():
            continue
        if extent is None:
            extent = QgsRectangle(e)
        else:
            extent.combineExtentWith(e)
    if extent is None:
        return None
    extent.scale(1.4)
    return extent


def add_label(layout, text, x, y, w, h, size=14, bold=False, color="#1a2332", align=Qt.AlignLeft):
    lbl = QgsLayoutItemLabel(layout)
    lbl.setText(text)
    f = QFont("Arial", size)
    f.setBold(bold)
    lbl.setFont(f)
    lbl.setFontColor(QColor(color))
    lbl.setHAlign(align)
    layout.addLayoutItem(lbl)
    lbl.attemptResize(QgsLayoutSize(w, h, QgsUnitTypes.LayoutMillimeters))
    lbl.attemptMove(QgsLayoutPoint(x, y, QgsUnitTypes.LayoutMillimeters))
    return lbl


def add_map(layout, x, y, w, h, layers_in_order, extent, satellite=None):
    mp = QgsLayoutItemMap(layout)
    mp.setRect(0, 0, w, h)
    layer_list = []
    if satellite:
        layer_list.append(satellite)
    layer_list += list(layers_in_order)
    mp.setLayers(layer_list)
    mp.setExtent(extent)
    mp.setBackgroundColor(QColor("#ffffff"))
    mp.setFrameEnabled(True)
    mp.setFrameStrokeColor(QColor("#1a2332"))
    mp.setFrameStrokeWidth(0.5)
    layout.addLayoutItem(mp)
    mp.attemptResize(QgsLayoutSize(w, h, QgsUnitTypes.LayoutMillimeters))
    mp.attemptMove(QgsLayoutPoint(x, y, QgsUnitTypes.LayoutMillimeters))
    return mp


def add_legend(layout, mp, layers_dict, x, y, w, h, title="Legend"):
    lg = QgsLayoutItemLegend(layout)
    lg.setLinkedMap(mp)
    lg.setTitle(title)
    lg.setAutoUpdateModel(False)
    root = QgsLayerTree()
    for name in layers_dict:
        root.addLayer(layers_dict[name])
    lg.model().setRootGroup(root)
    layout.addLayoutItem(lg)
    lg.attemptResize(QgsLayoutSize(w, h, QgsUnitTypes.LayoutMillimeters))
    lg.attemptMove(QgsLayoutPoint(x, y, QgsUnitTypes.LayoutMillimeters))
    return lg


def add_scale_bar(layout, mp, x, y):
    sb = QgsLayoutItemScaleBar(layout)
    sb.setLinkedMap(mp)
    sb.setStyle("Single Box")
    sb.setUnits(QgsUnitTypes.DistanceMeters)
    sb.setNumberOfSegments(2)
    sb.setNumberOfSegmentsLeft(0)
    sb.setUnitsPerSegment(25)
    sb.setUnitLabel("m")
    sb.applyDefaultSize()
    layout.addLayoutItem(sb)
    sb.attemptMove(QgsLayoutPoint(x, y, QgsUnitTypes.LayoutMillimeters))
    return sb


def add_north_arrow(layout, x, y, size=20):
    """Simple text-based North arrow (most reliable across QGIS versions)."""
    return add_label(layout, "N\n↑", x, y, size, size, size=14, bold=True, align=Qt.AlignCenter)


def add_calc_summary_panel(layout, x, y, w, h):
    """Static calc-model headline numbers — refresh manually when xlsx changes."""
    text = """\
<b>Project at a Glance</b><br/>
<br/>
<b>Water supply</b><br/>
Annual: ~10 million litres<br/>
Daily avg: 27,300 L<br/>
Storage: 24,000 L (3 tanks)<br/>
Buffer at peak: ~0.7 days<br/>
<br/>
<b>Productive area</b><br/>
Women's gardens: 4,047 m² (1 ac, 10 plots)<br/>
School garden: 2,023 m² (0.5 ac)<br/>
Total: 6,070 m²<br/>
<br/>
<b>Food output (annual)</b><br/>
~58 tonnes mixed vegetables<br/>
Leafy greens, tomato, okra<br/>
~400 people fed year-round<br/>
<br/>
<b>Efficiency wins</b><br/>
Drip + mulch + compost saves 61%<br/>
vs hand-watering baseline"""
    lbl = QgsLayoutItemLabel(layout)
    lbl.setMode(QgsLayoutItemLabel.ModeHtml)
    lbl.setText(text)
    f = QFont("Arial", 9)
    lbl.setFont(f)
    lbl.setMargin(4)
    lbl.setBackgroundEnabled(True)
    lbl.setBackgroundColor(QColor("#d9e1f2"))
    lbl.setFrameEnabled(True)
    lbl.setFrameStrokeColor(QColor("#1f4e78"))
    layout.addLayoutItem(lbl)
    lbl.attemptResize(QgsLayoutSize(w, h, QgsUnitTypes.LayoutMillimeters))
    lbl.attemptMove(QgsLayoutPoint(x, y, QgsUnitTypes.LayoutMillimeters))
    return lbl


# =============================================================
# LAYOUT 1 — Village Schematic (A2 landscape, no satellite)
# =============================================================
def build_village_layout(project, layers, extent):
    name = "Village Schematic"
    remove_existing_layout(project, name)
    layout = QgsPrintLayout(project)
    layout.initializeDefaults()
    layout.setName(name)
    page = layout.pageCollection().page(0)
    page.setPageSize("A2", QgsLayoutItemPolygon.Landscape if hasattr(QgsLayoutItemPolygon, 'Landscape') else 1)
    # A2 landscape = 594 × 420 mm
    PG_W, PG_H = 594, 420

    # Title block (top)
    add_label(layout, VILLAGE_TITLE, 15, 12, 564, 16, size=28, bold=True, color="#1f4e78")
    add_label(layout, VILLAGE_SUBTITLE, 15, 30, 564, 8, size=14, color="#444")

    # Map (most of the page)
    map_layers = [layers[k] for k in [
        "garden_plots", "school_buildings", "fence_areas", "solar_array",
        "water_towers", "infrastructure_points", "water_pipelines"
    ] if k in layers]
    mp = add_map(layout, 15, 45, 410, 340, map_layers, extent, satellite=None)

    # Legend (right column)
    lg_layers = {layers[k].name(): layers[k] for k in [
        "school_buildings", "garden_plots", "water_towers", "infrastructure_points",
        "water_pipelines", "solar_array", "fence_areas"
    ] if k in layers}
    add_legend(layout, mp, lg_layers, 435, 45, 145, 170, title="Ufunguo · Legend")

    # Scale + flow direction note
    add_scale_bar(layout, mp, 435, 225)
    add_label(layout, "↑ N\n(Kaskazini)", 545, 225, 35, 18, size=11, bold=True, align=Qt.AlignCenter)

    # Bilingual key terms
    glossary = """\
<b>Maneno muhimu · Key terms</b><br/>
Kisima — Borehole / well<br/>
Mnara wa Maji — Water tower<br/>
Tanki — Tank<br/>
Bomba — Pipe<br/>
Bustani — Garden<br/>
Shamba — Plot<br/>
Paneli za Jua — Solar panels<br/>
Uzio — Fence"""
    lbl = QgsLayoutItemLabel(layout)
    lbl.setMode(QgsLayoutItemLabel.ModeHtml)
    lbl.setText(glossary)
    lbl.setFont(QFont("Arial", 10))
    lbl.setMargin(3)
    lbl.setBackgroundEnabled(True)
    lbl.setBackgroundColor(QColor("#fff8d6"))
    lbl.setFrameEnabled(True)
    layout.addLayoutItem(lbl)
    lbl.attemptResize(QgsLayoutSize(145, 110, QgsUnitTypes.LayoutMillimeters))
    lbl.attemptMove(QgsLayoutPoint(435, 250, QgsUnitTypes.LayoutMillimeters))

    # Footer
    add_label(layout, VILLAGE_FOOTER, 15, 395, 564, 8, size=10, color="#666", align=Qt.AlignCenter)

    project.layoutManager().addLayout(layout)
    print(f"  Built layout: {name}")


# =============================================================
# LAYOUT 2 — Formal Report (A3 landscape, satellite base)
# =============================================================
def build_report_layout(project, layers, extent, satellite):
    name = "Formal Report"
    remove_existing_layout(project, name)
    layout = QgsPrintLayout(project)
    layout.initializeDefaults()
    layout.setName(name)
    page = layout.pageCollection().page(0)
    page.setPageSize("A3", 1)  # landscape
    PG_W, PG_H = 420, 297

    # Title block
    add_label(layout, REPORT_TITLE, 12, 10, 396, 12, size=22, bold=True, color="#1f4e78")
    add_label(layout, REPORT_SUBTITLE, 12, 24, 396, 7, size=12, color="#555")
    add_label(layout, "Date: ____  ·  CRS: EPSG:32736 (UTM 36S)", 12, 33, 396, 5, size=9, color="#777")

    # Big map (left 2/3)
    map_layers = [layers[k] for k in [
        "school_buildings", "garden_plots", "solar_array", "fence_areas",
        "water_towers", "infrastructure_points", "water_pipelines"
    ] if k in layers]
    mp = add_map(layout, 12, 45, 270, 220, map_layers, extent, satellite=satellite)

    # Legend
    lg_layers = {layers[k].name(): layers[k] for k in layers}
    add_legend(layout, mp, lg_layers, 290, 45, 118, 100, title="Legend")

    # Calc summary panel
    add_calc_summary_panel(layout, 290, 150, 118, 110)

    # Scale + north
    add_scale_bar(layout, mp, 14, 268)
    add_label(layout, "↑ N", 270, 268, 12, 8, size=12, bold=True, align=Qt.AlignCenter)

    # Footer
    add_label(layout, REPORT_FOOTER, 12, 285, 396, 6, size=8, color="#666", align=Qt.AlignCenter)

    project.layoutManager().addLayout(layout)
    print(f"  Built layout: {name}")


# =============================================================
# MAIN
# =============================================================
def main():
    project = QgsProject.instance()
    project.setCrs(QgsCoordinateReferenceSystem(PROJECT_CRS))
    print(f"Project CRS set to {PROJECT_CRS}")

    # Clear out previously loaded versions of these layers (so we don't duplicate)
    for layer in list(project.mapLayers().values()):
        if layer.name() in [c[1] for c in LAYER_CONFIG]:
            project.removeMapLayer(layer.id())

    print("Loading layers from gpkg...")
    layers = load_layers(project)
    if not layers:
        print("ERROR: no layers loaded. Check GPKG_PATH.")
        return

    print("Adding satellite basemap...")
    sat = add_satellite_basemap(project)

    print("Computing combined extent...")
    extent = compute_extent(layers)
    if extent is None:
        print("ERROR: no valid extent.")
        return
    print(f"  Extent: {extent}")

    print("Building Village Schematic layout...")
    build_village_layout(project, layers, extent)

    print("Building Formal Report layout...")
    build_report_layout(project, layers, extent, sat)

    print(f"Saving project to {PROJECT_FILE} ...")
    project.write(PROJECT_FILE)
    print("\nDONE. Open Project → Layouts to see them, or use Layout Manager.")
    print("Export each via: Layout → Export as PDF.")


main()
