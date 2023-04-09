"""
Utility methods and variables 
"""

import pathlib

# Output directory of esbuild
bundler_output_dir = pathlib.Path(__file__).parent / "static"

# Allowed default values
allowed_defaults = [
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
