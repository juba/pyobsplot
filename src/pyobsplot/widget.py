"""
Obsplot widget handling.
"""


import anywidget
import traitlets

from .utils import bundler_output_dir
from .parsing import SpecParser


class ObsplotWidget(anywidget.AnyWidget):
    """Obsplot widget class.

    It inherits from anywidget.Anywidget.

    The class takes a plot specification as input and generates a plot.

    The specification can be given as a dict, a Plot function call or as
    Python kwargs.
    """

    _esm = bundler_output_dir / "widget.js"
    _css = bundler_output_dir / "styles.css"
    # spec traitlet : plot specification
    spec = traitlets.Dict().tag(sync=True)

    def __init__(self, spec, debug: bool = False):
        """Obsplot widget constructor."""
        self._debug = debug
        # Init widget
        super().__init__(spec=spec)

    @traitlets.validate("spec")
    def _validate_spec(self, proposal):
        spec = proposal["value"]
        parser = SpecParser("widget")
        code = parser.parse(spec)
        spec = {"data": parser.serialize_data(), "code": code, "debug": self._debug}
        return spec
