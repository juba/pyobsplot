"""
Utility methods and variables.
"""

import pathlib

# Output directory of esbuild
bundler_output_dir = pathlib.Path(__file__).parent / "static"

# Minimum npm package version
MIN_NPM_VERSION = "0.4.2"

# Allowed default values
ALLOWED_DEFAULTS = [
    "marginTop",
    "marginRight",
    "marginBottom",
    "marginLeft",
    "margin",
    "width",
    "height",
    "aspectRatio",
    "style",
]

# Allowed format options
ALLOWED_FORMAT_OPTIONS = ["font", "scale", "margin", "legend-padding"]

# Themes
AVAILABLE_THEMES = ["light", "dark", "current"]
DEFAULT_THEME = "light"

# List of existing plot methods
# Generated by tools/get_plot_methods.js
PLOT_METHODS = (
    "Area",
    "Arrow",
    "BarX",
    "BarY",
    "Cell",
    "Contour",
    "Density",
    "Dot",
    "Frame",
    "Geo",
    "Hexgrid",
    "Image",
    "Line",
    "Link",
    "Mark",
    "Raster",
    "Rect",
    "RuleX",
    "RuleY",
    "Text",
    "TickX",
    "TickY",
    "Tip",
    "Vector",
    "area",
    "areaX",
    "areaY",
    "arrow",
    "auto",
    "autoSpec",
    "axisFx",
    "axisFy",
    "axisX",
    "axisY",
    "barX",
    "barY",
    "bin",
    "binX",
    "binY",
    "bollinger",
    "bollingerX",
    "bollingerY",
    "boxX",
    "boxY",
    "cell",
    "cellX",
    "cellY",
    "centroid",
    "circle",
    "cluster",
    "column",
    "contour",
    "crosshair",
    "crosshairX",
    "crosshairY",
    "delaunayLink",
    "delaunayMesh",
    "density",
    "differenceY",
    "dodgeX",
    "dodgeY",
    "dot",
    "dotX",
    "dotY",
    "filter",
    "find",
    "formatIsoDate",
    "formatMonth",
    "formatNumber",
    "formatWeekday",
    "frame",
    "geo",
    "geoCentroid",
    "graticule",
    "gridFx",
    "gridFy",
    "gridX",
    "gridY",
    "group",
    "groupX",
    "groupY",
    "groupZ",
    "hexagon",
    "hexbin",
    "hexgrid",
    "hull",
    "identity",
    "image",
    "indexOf",
    "initializer",
    "interpolateNearest",
    "interpolateNone",
    "interpolatorBarycentric",
    "interpolatorRandomWalk",
    "legend",
    "line",
    "lineX",
    "lineY",
    "linearRegressionX",
    "linearRegressionY",
    "link",
    "map",
    "mapX",
    "mapY",
    "marks",
    "normalize",
    "normalizeX",
    "normalizeY",
    "numberInterval",
    "plot",
    "pointer",
    "pointerX",
    "pointerY",
    "raster",
    "rect",
    "rectX",
    "rectY",
    "reverse",
    "ruleX",
    "ruleY",
    "scale",
    "select",
    "selectFirst",
    "selectLast",
    "selectMaxX",
    "selectMaxY",
    "selectMinX",
    "selectMinY",
    "shiftX",
    "shuffle",
    "sort",
    "sphere",
    "spike",
    "stackX",
    "stackX1",
    "stackX2",
    "stackY",
    "stackY1",
    "stackY2",
    "text",
    "textX",
    "textY",
    "tickX",
    "tickY",
    "timeInterval",
    "tip",
    "transform",
    "tree",
    "treeLink",
    "treeNode",
    "utcInterval",
    "valueof",
    "vector",
    "vectorX",
    "vectorY",
    "voronoi",
    "voronoiMesh",
    "window",
    "windowX",
    "windowY",
)
