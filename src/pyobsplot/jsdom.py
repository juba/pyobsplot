"""
Obsplot jsdom handling.
"""

import subprocess
import json
import shutil
from IPython.display import HTML, SVG

from typing import Any, Optional

from .utils import exec_path
from .parsing import SpecParser


class ObsplotJsdom:
    """Obsplot JSDom class.

    The class takes a plot specification as input and generates a plot as SVG or HTML
    by calling a JSDom script with node.

    The specification can be given as a dict, a Plot function call or as
    Python kwargs.
    """

    def __init__(self, spec: Any) -> None:
        """
        Constructor. Parse the spec given as argument.
        """
        # Create parser
        parser = SpecParser("jsdom")
        # Parse spec code
        code = parser.parse(spec)
        # Create spec object
        spec = {"data": parser.serialize_data(), "code": code}
        self.spec = spec

    def plot(self) -> Optional[HTML | SVG]:
        """Generates the plot by calling node script.

        Returns:
            Optional[HTML | SVG]: either an HTML or SVG IPython.display object.
        """

        # Check for node executable
        node = shutil.which("node")
        if not node:
            raise RuntimeError("node executable has not been found.")
        jsdom_path = exec_path("pyobsplot-jsdom")
        # Run node script with JSON spec as input
        p = subprocess.run(
            jsdom_path,
            input=json.dumps(self.spec),
            capture_output=True,
            encoding="Utf8",
        )
        if p.returncode != 0:
            raise RuntimeError("jsdom script error: " + p.stderr)
        # Get script output
        out = p.stdout
        # If output is svg, returns IPython.display.SVG
        if out[0:4] == "<svg":
            return SVG(out)
        # Else, returns IPython.display.HTML
        else:
            out = "<div class='pyobsplot-plot'>" + p.stdout + "</div>"
            return HTML(out)
