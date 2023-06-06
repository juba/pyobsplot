"""
Obsplot jsdom handling.
"""

import json
import requests
from IPython.display import HTML, SVG  # type: ignore


from typing import Any

from .parsing import SpecParser
from .utils import default_theme


class ObsplotJsdom:
    """Obsplot JSDom class.

    The class takes a plot specification as input and generates a plot as SVG or HTML
    by calling a JSDom script with node.

    The specification can be given as a dict, a Plot function call or as
    Python kwargs.
    """

    def __init__(
        self,
        spec: Any,
        port: int,
        theme: str = default_theme,
        default: dict = {},
        debug: bool = False,
    ) -> None:
        """
        Constructor. Parse the spec given as argument.
        """
        # Create parser
        parser = SpecParser(renderer="jsdom", default=default)
        # Parse spec code
        parser.spec = spec
        code = parser.parse_spec()
        # Create spec object
        spec = {"data": parser.serialize_data(), "code": code, "debug": debug}
        self.spec = spec
        self.port = port
        self.theme = theme

    def plot(self):
        """Generates the plot by sending request to http node server.

        Returns:
            Either an HTML or SVG IPython.display object.
        """

        # Make POST request with plot spec
        url = f"http://localhost:{self.port}/plot"
        try:
            r = requests.post(
                url, data=json.dumps({"spec": self.spec, "theme": self.theme})
            )
        except ConnectionRefusedError:
            print(
                f"Error: can't connect to generator server on port {self.port}. Please recreate your generator object."  # noqa: E501
            )
        # Read back result
        if r.status_code == 500:  # type: ignore
            raise RuntimeError(r.content.decode())  # type: ignore
        out = r.content.decode()  # type: ignore

        # If output is svg, returns IPython.display.SVG
        if out[0:4] == "<svg":
            return SVG(out)
        # Else, returns IPython.display.HTML
        else:
            return HTML(out)
