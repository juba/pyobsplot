"""
Obsplot widget handling.
"""


import pathlib
import anywidget
import traitlets

from .parsing import parse_spec

# Output directory of esbuild
bundler_output_dir = pathlib.Path("static")


class Obsplot(anywidget.AnyWidget):
    """Obsplot widget class.

    It inherits from anywidget.Anywidget.

    The class takes a plot specification as input and generates a plot.

    The specification can be given as a dict, a Plot function call or as
    Python kwargs.
    """

    _esm = bundler_output_dir / "index.js"
    _css = bundler_output_dir / "index.css"
    # spec traitlet : plot specification
    spec = traitlets.Dict().tag(sync=True)

    def __init__(self, *args, **kwargs):
        if len(args) == 1 and len(kwargs) == 0:
            spec = args[0]
        elif len(args) == 0 and len(kwargs) == 1 and "spec" in kwargs:
            spec = kwargs["spec"]
        elif len(args) == 0 and len(kwargs) > 0:
            spec = kwargs
        else:
            ValueError("Incorrect ObsPlot arguments")
        super().__init__(spec=spec)

    @traitlets.validate("spec")
    def _validate_spec(self, proposal):
        spec = proposal["value"]
        spec = parse_spec(spec)
        return spec
