"""
Obsplot widget handling.
"""


from typing import Optional

import anywidget
import traitlets

from pyobsplot.parsing import SpecParser
from pyobsplot.utils import DEFAULT_THEME, bundler_output_dir


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
        bundler_output_dir / "static-widget.js", start_thread=False
    )
    _css = anywidget._file_contents.FileContents(  # type: ignore
        bundler_output_dir / "static-styles.css", start_thread=False
    )
    # spec traitlet : plot specification
    spec = traitlets.Dict().tag(sync=True)

    def __init__(
        self,
        spec,
        theme: str = DEFAULT_THEME,
        default: Optional[dict] = None,
        debug: bool = False,  # noqa: FBT001, FBT002
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
