"""
Chipanga QField project builder.

HOW TO RUN:
  1. Open QGIS.
  2. Open this folder (the one containing chipanga.gpkg + this script).
  3. In QGIS: Plugins → Python Console → Show Editor → Open this file → Run (green ▶).
  4. When done you'll have chipanga.qgz next to chipanga.gpkg, ready for QFieldSync.

This script:
  - Loads all 7 feature layers from chipanga.gpkg
  - Configures attribute forms (dropdowns, photo widget, default values, expressions)
  - Adds ESRI World Imagery satellite basemap
  - Styles each layer with sensible colors/labels
  - Sets project CRS to EPSG:4326
  - Saves chipanga.qgz
"""

import os
from qgis.core import (
    QgsProject, QgsVectorLayer, QgsRasterLayer, QgsCoordinateReferenceSystem,
    QgsEditorWidgetSetup, QgsFieldConstraints, QgsDefaultValue,
    QgsSymbol, QgsRendererCategory, QgsCategorizedSymbolRenderer,
    QgsPalLayerSettings, QgsTextFormat, QgsVectorLayerSimpleLabeling,
    QgsLineSymbol, QgsFillSymbol, QgsMarkerSymbol,
)
from qgis.PyQt.QtGui import QColor, QFont

# -------------------------------------------------------------------
# Resolve folder of this script — chipanga.gpkg should sit next to it
# -------------------------------------------------------------------
HERE = os.path.dirname(os.path.abspath(__file__)) if '__file__' in globals() else os.path.dirname(QgsProject.instance().fileName()) or os.getcwd()
GPKG = os.path.join(HERE, 'chipanga.gpkg')
QGZ_OUT = os.path.join(HERE, 'chipanga.qgz')
assert os.path.exists(GPKG), f'chipanga.gpkg not found next to this script: {GPKG}'

print(f'Building project from: {GPKG}')

project = QgsProject.instance()
project.clear()
project.setCrs(QgsCoordinateReferenceSystem('EPSG:4326'))
project.setTitle('Chipanga A Water + Gardens Project')

# Site center (school centroid) — used to nudge the canvas there
SITE_LON, SITE_LAT = 35.34560, -6.23740

# -------------------------------------------------------------------
# Layer config: each entry defines table name, geometry type, label
# field, color, and per-field widget setups.
# -------------------------------------------------------------------
def vmap(pairs):
    """Build ValueMap config from list of (label, value) pairs."""
    return {'map': [{label: value} for (label, value) in pairs]}

PHOTO_WIDGET = QgsEditorWidgetSetup('ExternalResource', {
    'FileWidget': True, 'FileWidgetButton': True,
    'DocumentViewer': 1,                # 1 = Image
    'DocumentViewerHeight': 0,
    'DocumentViewerWidth': 0,
    'RelativeStorage': 1,               # relative to project file
    'StorageMode': 0,                   # files
    'PropertyCollection': {'name': '', 'properties': {}, 'type': 'collection'},
    'StorageType': '',
    'PropertyCollection': {'name': None, 'properties': {}, 'type': 'collection'},
})

LAYERS = [
    {
        'name': 'school_buildings', 'label': 'School Buildings', 'geom': 'Polygon',
        'fill': '#f7c948', 'stroke': '#7a5b00', 'label_field': 'building_id',
        'reuse_last': ['roof_type', 'condition'],
        'widgets': {
            'building_use': ('ValueMap', vmap([
                ('Classroom','classroom'), ('Office','office'), ('Head teacher office','head-office'),
                ('Kitchen','kitchen'), ('Dining hall','dining-hall'), ('Library','library'),
                ('Latrine','latrine'), ('Dorm','dorm'), ('Storage','storage'), ('Other','other'),
            ])),
            'roof_type': ('ValueMap', vmap([
                ('Iron sheet','iron-sheet'), ('Thatch','thatch'),
                ('Tile','tile'), ('Concrete','concrete'), ('Other','other'),
            ])),
            'condition': ('ValueMap', vmap([
                ('Good','good'), ('Fair','fair'), ('Poor','poor'), ('Derelict','derelict'),
            ])),
            'photo_path': ('ExternalResource', None),
        },
    },
    {
        'name': 'garden_plots', 'label': 'Garden Plots', 'geom': 'Polygon',
        'fill': '#7ec850', 'stroke': '#2e5d1f', 'label_field': 'plot_id',
        'reuse_last': ['group_name', 'use_type', 'irrigation_method'],
        'expression_defaults': {'area_m2': '$area'},
        'widgets': {
            'group_name': ('ValueMap', vmap([
                ("Women's group",'womens-group'), ('School','school'),
                ('Communal','communal'), ('Other','other'),
            ])),
            'use_type': ('ValueMap', vmap([
                ('Vegetables','vegetables'), ('Fruit','fruit'),
                ('Mixed','mixed'), ('Fallow','fallow'), ('Other','other'),
            ])),
            'irrigation_method': ('ValueMap', vmap([
                ('Drip','drip'), ('Hand-watering','hand'), ('None','none'), ('Other','other'),
            ])),
            'photo_path': ('ExternalResource', None),
        },
    },
    {
        'name': 'fence_areas', 'label': 'Fence Areas', 'geom': 'Polygon',
        'fill': '#cccccc88', 'stroke': '#666666', 'label_field': 'fence_id',
        'reuse_last': ['fence_type', 'condition'],
        'expression_defaults': {'length_m': '$perimeter'},
        'widgets': {
            'fence_purpose': ('ValueMap', vmap([
                ('Well protection','well-protection'), ('Garden protection','garden-protection'),
                ('Livestock exclusion','livestock-exclusion'), ('Other','other'),
            ])),
            'fence_type': ('ValueMap', vmap([
                ('Chain link','chain-link'), ('Barbed wire','barbed-wire'),
                ('Wooden','wooden'), ('Thorn brush','thorn-brush'),
                ('Woven mesh','woven-mesh'), ('Other','other'),
            ])),
            'condition': ('ValueMap', vmap([
                ('Good','good'), ('Fair','fair'), ('Poor','poor'), ('Derelict','derelict'),
            ])),
            'photo_path': ('ExternalResource', None),
        },
    },
    {
        'name': 'solar_array', 'label': 'Solar Array', 'geom': 'Polygon',
        'fill': '#1f3a93', 'stroke': '#0d1f4f', 'label_field': 'array_id',
        'reuse_last': ['mounting'],
        'expression_defaults': {'total_watts': 'panel_count * panel_watts'},
        'widgets': {
            'mounting': ('ValueMap', vmap([
                ('Ground','ground'), ('Pole','pole'),
                ('Roof','roof'), ('Other','other'),
            ])),
            'photo_path': ('ExternalResource', None),
        },
    },
    {
        'name': 'water_towers', 'label': 'Water Towers', 'geom': 'Point',
        'color': '#0099cc', 'size': 6.0, 'label_field': 'tower_id',
        'reuse_last': ['serves', 'material'],
        'widgets': {
            'serves': ('ValueMap', vmap([
                ('School (4,000 L)','school'),
                ("Women's garden (10,000 L)",'womens-garden'),
                ('School garden (10,000 L)','school-garden'),
                ('Multiple','multiple'), ('Other','other'),
            ])),
            'material': ('ValueMap', vmap([
                ('Concrete','concrete'), ('Steel','steel'),
                ('Plastic','plastic'), ('Brick','brick'), ('Other','other'),
            ])),
            'photo_path': ('ExternalResource', None),
        },
    },
    {
        'name': 'infrastructure_points', 'label': 'Infrastructure Points', 'geom': 'Point',
        'color': '#e91e63', 'size': 4.5, 'label_field': 'feature_type',
        'reuse_last': ['feature_type', 'status'],
        'widgets': {
            'feature_type': ('ValueMap', vmap([
                ('Borehole','borehole'), ('Well pump','well-pump'),
                ('Gate valve','gate-valve'), ('Water meter','water-meter'),
                ('Junction','junction'), ('Elbow fitting','elbow'),
                ('Saddle','saddle'), ('End plug','end-plug'),
                ('Other fitting','other-fitting'), ('Other','other'),
            ])),
            'status': ('ValueMap', vmap([
                ('Working','working'), ('Broken','broken'),
                ('Planned','planned'), ('Unknown','unknown'),
            ])),
            'photo_path': ('ExternalResource', None),
        },
    },
    {
        'name': 'water_pipelines', 'label': 'Water Pipelines', 'geom': 'Line',
        'color': '#9c27b0', 'width': 0.7, 'label_field': 'pipe_type',
        'reuse_last': ['pipe_type', 'material', 'buried'],
        'expression_defaults': {'length_m': '$length'},
        'widgets': {
            'pipe_type': ('ValueMap', vmap([
                ('Mainline','mainline'), ('Submain','submain'),
                ('Dripline','dripline'), ('Distribution','distribution'), ('Other','other'),
            ])),
            'material': ('ValueMap', vmap([
                ('HDPE','HDPE'), ('PVC','PVC'), ('PE','PE'),
                ('GI (galvanised iron)','GI'), ('Copper','copper'), ('Other','other'),
            ])),
            'buried': ('ValueMap', vmap([
                ('Yes','yes'), ('No','no'), ('Partial','partial'),
            ])),
            'photo_path': ('ExternalResource', None),
        },
    },
]

# -------------------------------------------------------------------
# Satellite basemap — try a chain of providers, use the first that loads.
# Google Satellite is preferred for Tanzania (Maxar-sourced, very high res,
# no API key required). QFieldSync caches the active basemap to MBTiles
# during packaging so it works offline on Charlie's phone.
# -------------------------------------------------------------------
basemap_options = [
    ('Google Satellite',
     'type=xyz&url=https://mt1.google.com/vt/lyrs%3Ds%26x%3D%7Bx%7D%26y%3D%7By%7D%26z%3D%7Bz%7D&zmax=20&zmin=0'),
    ('Google Hybrid (satellite + labels)',
     'type=xyz&url=https://mt1.google.com/vt/lyrs%3Dy%26x%3D%7Bx%7D%26y%3D%7By%7D%26z%3D%7Bz%7D&zmax=20&zmin=0'),
    ('ESRI World Imagery',
     'type=xyz&url=https://server.arcgisonline.com/ArcGIS/rest/services/World_Imagery/MapServer/tile/%7Bz%7D/%7By%7D/%7Bx%7D&zmax=19&zmin=0'),
]
basemap = None
for bname, burl in basemap_options:
    layer = QgsRasterLayer(burl, bname, 'wms')
    if layer.isValid():
        project.addMapLayer(layer, addToLegend=True)
        print(f'  + basemap: {bname}')
        basemap = layer
        break
    else:
        print(f'  - skipped {bname} (not valid in this QGIS install)')

if basemap is None:
    print('  ! No basemap loaded automatically. Add manually:')
    print('      QGIS Browser panel → XYZ Tiles → right-click → New Connection')
    print('      Name: Google Satellite')
    print('      URL:  https://mt1.google.com/vt/lyrs=s&x={x}&y={y}&z={z}')
    print('      Max zoom: 20')

# -------------------------------------------------------------------
# Load and configure each vector layer
# -------------------------------------------------------------------
for cfg in LAYERS:
    uri = f"{GPKG}|layername={cfg['name']}"
    lyr = QgsVectorLayer(uri, cfg['label'], 'ogr')
    if not lyr.isValid():
        print(f"  ! FAILED: {cfg['name']}")
        continue
    project.addMapLayer(lyr)
    print(f"  + layer: {cfg['label']}")

    # Form widgets
    for fname, (wtype, wcfg) in cfg.get('widgets', {}).items():
        idx = lyr.fields().indexOf(fname)
        if idx == -1:
            print(f"    ! field {fname} missing on {cfg['name']}")
            continue
        if wtype == 'ExternalResource':
            lyr.setEditorWidgetSetup(idx, PHOTO_WIDGET)
        else:
            lyr.setEditorWidgetSetup(idx, QgsEditorWidgetSetup(wtype, wcfg))

    # Reuse-last-value: tells QField to remember the previous entry on these fields
    efc = lyr.editFormConfig()
    for fname in cfg.get('reuse_last', []):
        idx = lyr.fields().indexOf(fname)
        if idx != -1:
            efc.setReuseLastValue(idx, True)
    lyr.setEditFormConfig(efc)

    # Expression-based defaults (e.g., area_m2 = $area)
    for fname, expr in cfg.get('expression_defaults', {}).items():
        idx = lyr.fields().indexOf(fname)
        if idx != -1:
            lyr.setDefaultValueDefinition(idx, QgsDefaultValue(expr, True))

    # Styling
    geom = cfg['geom']
    if geom == 'Polygon':
        sym = QgsFillSymbol.createSimple({
            'color': cfg['fill'].replace('#','') if not cfg['fill'].startswith('#') else cfg['fill'],
            'outline_color': cfg['stroke'],
            'outline_width': '0.5',
            'style': 'solid',
        })
        sym.setOpacity(0.55)
        lyr.renderer().setSymbol(sym)
    elif geom == 'Point':
        sym = QgsMarkerSymbol.createSimple({
            'name': 'circle',
            'color': cfg['color'],
            'outline_color': '#222222',
            'outline_width': '0.4',
            'size': str(cfg.get('size', 4)),
        })
        lyr.renderer().setSymbol(sym)
    elif geom == 'Line':
        sym = QgsLineSymbol.createSimple({
            'color': cfg['color'], 'width': str(cfg.get('width', 0.6)),
        })
        lyr.renderer().setSymbol(sym)

    # Labels
    if cfg.get('label_field'):
        pal = QgsPalLayerSettings()
        pal.fieldName = cfg['label_field']
        pal.enabled = True
        text_fmt = QgsTextFormat()
        text_fmt.setFont(QFont('Arial', 9))
        text_fmt.setSize(9)
        pal.setFormat(text_fmt)
        lyr.setLabeling(QgsVectorLayerSimpleLabeling(pal))
        lyr.setLabelsEnabled(True)

    lyr.triggerRepaint()

# -------------------------------------------------------------------
# Save .qgz
# -------------------------------------------------------------------
ok = project.write(QGZ_OUT)
print(f"\nProject saved: {QGZ_OUT}  (ok={ok})")
print('\nNext steps:')
print('  1. Plugins → Manage and Install Plugins → install "QFieldSync"')
print('  2. QField → Package for QField → choose this folder, enable "Cache map tiles"')
print('     for the ESRI World Imagery layer (so the satellite works offline)')
print('  3. Copy the resulting folder to Charlie\'s phone')
