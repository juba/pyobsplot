"""
Utility methods and variables.
"""

import pathlib

# Output directory of esbuild
bundler_output_dir = pathlib.Path(__file__).parent / "static"

# Minimum npm package version
MIN_NPM_VERSION = "0.5.0"

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
