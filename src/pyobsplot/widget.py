"""
Obsplot widget handling.
"""


import anywidget
import traitlets

from .utils import bundler_output_dir, default_theme
from .parsing import SpecParser


class ObsplotWidget(anywidget.AnyWidget):
    """Obsplot widget class.

    It inherits from anywidget.Anywidget.

    The class takes a plot specification as input and generates a plot.

    The specification can be given as a dict, a Plot function call or as
    Python kwargs.
    """

    # Disable _esm and _css watching and live reload to avoid "exception not rethrown"
    # error with pytest.
    _esm = anywidget._file_contents.FileContents(  # type: ignore
        bundler_output_dir / "widget.js", start_thread=False
    )
    _css = anywidget._file_contents.FileContents(  # type: ignore
        bundler_output_dir / "styles.css", start_thread=False
    )
    # spec traitlet : plot specification
    spec = traitlets.Dict().tag(sync=True)

    def __init__(
        self, spec, theme: str = default_theme, default: dict = {}, debug: bool = False
    ):
        """Obsplot widget constructor."""
        self._debug = debug
        self._default = default
        self._theme = theme
        # Init widget
        super().__init__(spec=spec)

    @traitlets.validate("spec")
    def _validate_spec(self, proposal):
        spec = proposal["value"]
        parser = SpecParser(renderer="widget", default=self._default)
        parser.spec = spec
        code = parser.parse_spec()
        spec = {
            "data": parser.serialize_data(),
            "code": code,
            "debug": self._debug,
            "theme": self._theme,
        }
        return spec
