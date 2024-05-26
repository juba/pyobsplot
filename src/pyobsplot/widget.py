"""
Obsplot widget handling.
"""

from typing import Any

import anywidget
import traitlets

from pyobsplot.parsing import SpecParser
from pyobsplot.utils import DEFAULT_THEME, bundler_output_dir


class ObsplotWidget(anywidget.AnyWidget):

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
        *,
        spec: Any,
        theme: str = DEFAULT_THEME,
        default: dict | None = None,
        debug: bool = False,
    ) -> None:
        """
        Obsplot widget class, inherits from anywidget.Anywidget.

        Parameters
        ----------
        spec : Any
            Plot specification as dict, Plot function call or Python kwargs.
        theme : {'light', 'dark', 'current'}, optional
            color theme to use, by default 'light'
        default : dict, optional
            dict of default spec values, by default None
        debug : bool, optional
            activate debug mode, by default False
        """
        self._debug = debug
        self._default = default
        self._theme = theme
        # Init widget
        super().__init__(spec=spec)

    @traitlets.validate("spec")
    def _validate_spec(self, proposal):
        spec = proposal["value"]
        parser = SpecParser(renderer="widget", default=self._default)
        parser.set_spec(spec)
        code = parser.parse_spec()
        spec = {
            "data": parser.serialize_data(),
            "code": code,
            "debug": self._debug,
            "theme": self._theme,
        }
        return spec
