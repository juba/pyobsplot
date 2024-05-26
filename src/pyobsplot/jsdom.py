"""
Obsplot jsdom handling.
"""

import json
import warnings
from typing import Any

import requests
from IPython.display import HTML, SVG

from pyobsplot.parsing import SpecParser
from pyobsplot.utils import DEFAULT_THEME

HTTP_SERVER_ERROR = 500


class ObsplotJsdom:

    def __init__(
        self,
        *,
        spec: Any,
        port: int,
        theme: str = DEFAULT_THEME,
        default: dict | None = None,
        debug: bool = False,
        force_figure: bool = False,
    ) -> None:
        """
        Obsplot JSDom class. The class takes a plot specification as input and generates
        a plot as SVG or HTML by calling a JSDom script with node.

        Parameters
        ----------
        spec : Any
            Plot specification as dict, Plot function call or Python kwargs.
        port : int
            port number of the jsdom server.
        theme : {'light', 'dark', 'current'}, optional
            color theme to use, by default 'light'
        default : dict, optional
            dict of default spec values, by default None
        debug : bool, optional
            activate debug mode, by default False
        force_figure : bool, optional
            if True, set figure to true in plot specification, by default False
        """

        # Create parser
        parser = SpecParser(renderer="jsdom", default=default)
        # Parse spec code
        parser.set_spec(spec, force_figure=force_figure)
        code = parser.parse_spec()
        # Create spec object
        spec = {"data": parser.serialize_data(), "code": code, "debug": debug}
        self.spec = spec
        self.port = port
        self.theme = theme

    def plot(self) -> SVG | HTML:
        """
        Generates the plot by sending request to http node server.

        Returns
        -------
        HTML | SVG
            Either an HTML or SVG IPython.display object.
        """

        # Make POST request with plot spec
        url = f"http://localhost:{self.port}/plot"
        try:
            r = requests.post(
                url,
                data=json.dumps({"spec": self.spec, "theme": self.theme}),
                timeout=600,
            )
        except ConnectionRefusedError:
            msg = (
                f"Error: can't connect to generator server on port {self.port}.\n"
                f"Please recreate your generator object."
            )
            warnings.warn(msg, stacklevel=1)
        # Read back result
        if r.status_code == HTTP_SERVER_ERROR:  # type: ignore
            raise RuntimeError(r.content.decode())  # type: ignore
        out = r.content.decode()  # type: ignore

        # If output is svg, returns IPython.display.SVG
        if out[0:4] == "<svg":
            return SVG(out)
        # Else, returns IPython.display.HTML
        else:
            return HTML(out)
