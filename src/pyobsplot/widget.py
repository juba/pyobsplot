"""
Obsplot widget handling.
"""


import anywidget
import traitlets

from .utils import bundler_output_dir, available_themes, default_theme
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
    # theme traitlet : plot theme (dark, light or current)
    theme = traitlets.Unicode().tag(sync=True)

    def __init__(
        self, spec, theme: str = default_theme, default: dict = {}, debug: bool = False
    ):
        """Obsplot widget constructor."""
        self._debug = debug
        self._default = default
        # Init widget
        super().__init__(spec=spec, theme=theme)

    @traitlets.validate("spec")
    def _validate_spec(self, proposal):
        spec = proposal["value"]
        parser = SpecParser(renderer="widget", default=self._default)
        parser.spec = spec
        code = parser.parse_spec()
        spec = {"data": parser.serialize_data(), "code": code, "debug": self._debug}
        return spec

    @traitlets.validate("theme")
    def _validate_theme(self, proposal):
        new_theme = proposal["value"]
        if new_theme not in available_themes:
            new_theme = default_theme
        return new_theme
