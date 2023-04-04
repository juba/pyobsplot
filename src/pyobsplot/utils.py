"""
Utility methods and variables 
"""

import pathlib

# Output directory of esbuild
bundler_output_dir = pathlib.Path(__file__).parent / "static"
# Default renderer
default_renderer = "widget"
available_renderers = ["widget", "jsdom"]
