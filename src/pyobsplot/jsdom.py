"""
Obsplot jsdom handling.
"""

import subprocess
import json
from IPython.display import HTML, SVG

from .obsplot import bundler_output_dir
from .parsing import SpecParser


class ObsplotJsdom:
    """Obsplot JSDom class.

    The class takes a plot specification as input and generates a plot as SVG or HTML
    by calling a JSDom script with node.

    The specification can be given as a dict, a Plot function call or as
    Python kwargs.
    """

    def __init__(self, spec):
        parser = SpecParser("jsdom")
        code = parser.parse(spec)
        spec = {"data": parser.serialize_data(), "code": code}
        self.spec = spec

    def plot(self):
        path = bundler_output_dir / "jsdom.js"
        p = subprocess.run(
            ["node", path],
            input=json.dumps(self.spec),
            capture_output=True,
            encoding="Utf8",
        )
        if p.returncode != 0:
            raise RuntimeError("jsdom script error: " + p.stderr)
        out = p.stdout
        if out[0:4] == "<svg":
            return SVG(out)
        else:
            out = "<div class='pyobsplot-plot'>" + p.stdout + "</div>"
            return HTML(out)
