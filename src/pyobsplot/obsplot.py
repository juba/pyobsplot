"""
Obsplot main class.
"""

import io
import os
import shutil
import signal
import warnings
from pathlib import Path
from subprocess import PIPE, Popen, SubprocessError
from typing import Any, Optional, Union

from IPython.display import HTML, SVG, display
from ipywidgets.embed import embed_minimal_html

from pyobsplot.jsdom import ObsplotJsdom
from pyobsplot.utils import (
    ALLOWED_DEFAULTS,
    AVAILABLE_THEMES,
    DEFAULT_THEME,
    MIN_NPM_VERSION,
)
from pyobsplot.widget import ObsplotWidget


class Obsplot:
    """
    Main Obsplot class.

    Launches a Jupyter widget with ObsplotWidget class, or displays an IPython display
    with ObsplotJsdom depending on the renderer.
    """

    def __new__(
        cls,
        renderer: str = "widget",
        theme: str = DEFAULT_THEME,
        default: Optional[dict] = None,
        debug: bool = False,  # noqa: FBT001, FBT002
    ) -> Any:
        """
        Main Obsplot class constructor. Returns a Creator instance depending on the
        renderer passed as argument.

        Args:
            renderer (str): renderer to be used.
            theme (str): color theme to use, can be "light" (default), "dark" or
                "current".
            default (dict): dict of default spec values.
            debug (bool): if True, activate debug mode (for widget renderer only)

        returns:
            A Creator object of type depending of the renderer.
        """

        # Check theme value
        if theme not in AVAILABLE_THEMES:
            msg = f"""
                Incorrect theme '{theme}'.
                Available renderers are {AVAILABLE_THEMES}
                """
            raise ValueError(msg)

        # Check renderer value
        available_renderers = ["widget", "jsdom"]

        # Plot spec with the configured renderer
        if renderer == "widget":
            return ObsplotWidgetCreator(theme=theme, default=default, debug=debug)
        elif renderer == "jsdom":
            return ObsplotJsdomCreator(theme=theme, default=default, debug=debug)
        else:
            msg = f"""
                Incorrect renderer '{renderer}'.
                Available renderers are {available_renderers}
                """
            raise ValueError(msg)


class ObsplotCreator:
    """
    Creator class.
    """

    def __init__(
        self,
        theme: str = DEFAULT_THEME,
        default: Optional[dict] = None,
        debug: bool = False,  # noqa: FBT001, FBT002
    ) -> None:
        """Generic Creator constructor

        Args:
            default (dict, optional): dict of default spec values. Defaults to {}.
        """
        if default is None:
            default = {}
        for k in default:
            if k not in ALLOWED_DEFAULTS:
                msg = f"{k} is not allowed in default.\nAllowed values: {ALLOWED_DEFAULTS}."  # noqa: E501
                raise ValueError(msg)
        self._default = default
        self._debug = debug
        self._theme = theme

    def __repr__(self):
        return (
            f"<{type(self).__name__}>\n"
            f"theme: {self._theme!r}\n"
            f"debug: {self._debug!r}\n"
            f"default: {self._default!r}\n"
        )

    @property
    def theme(self):
        return self._theme

    @theme.setter
    def theme(self, val):
        self._theme = val

    @property
    def default(self):
        return self._default

    @default.setter
    def default(self, val):
        self._default = val

    def get_spec(self, *args, **kwargs):
        """
        Extract plot specification from args and kwargs, taking into account
        the alternative specification syntaxes.
        """

        # Only one dict arg -> spec passed as dict
        if len(args) == 1 and len(kwargs) == 0 and isinstance(args[0], dict):
            spec = args[0]
        # Only one kwarg called spec
        elif len(args) == 0 and len(kwargs) == 1 and "spec" in kwargs:
            spec = kwargs["spec"]
        # Only kwargs -> spec is kwargs
        elif len(args) == 0 and len(kwargs) > 0:
            spec = kwargs
        # No arguments given
        elif len(args) == 0 and len(kwargs) == 0:
            msg = "Missing plot specification"
            raise ValueError(msg)
        else:
            msg = "Incorrect plot specification"
            raise ValueError(msg)
        return spec


class ObsplotWidgetCreator(ObsplotCreator):
    """
    Widget renderer Creator class.
    """

    def __init__(
        self,
        theme: str = DEFAULT_THEME,
        default: Optional[dict] = None,
        debug: bool = False,  # noqa: FBT001, FBT002
    ) -> None:
        super().__init__(theme, default, debug)

    def __call__(self, *args, **kwargs) -> Optional[ObsplotWidget]:
        """
        Method called when an instance is called.
        """
        path = None
        if "path" in kwargs:
            path = kwargs["path"]
            del kwargs["path"]
        spec = self.get_spec(*args, **kwargs)
        res = ObsplotWidget(
            spec, theme=self._theme, default=self._default, debug=self._debug
        )  # type: ignore
        if path is not None:
            ObsplotWidgetCreator.save_to_file(path, res)
        else:
            return res

    @staticmethod
    def save_to_file(path: str, res: ObsplotWidget) -> None:
        """
        Save an Obsplot object generated by a widget creator to a file.

        Args:
            path (str): path to output file.
            res (ObsplotWidget): result of a call to Obsplot().
        """
        extension = Path(path).suffix.lower()
        if extension not in [".html", ".htm"]:
            warnings.warn(
                "Output file extension should be one of 'html' or 'htm'",
                RuntimeWarning,
                stacklevel=1,
            )
        embed_minimal_html(path, views=[res], drop_defaults=False)


class ObsplotJsdomCreator(ObsplotCreator):
    """
    Jsdom renderer Creator class.
    """

    def __init__(
        self,
        theme: str = DEFAULT_THEME,
        default: Optional[dict] = None,
        debug: bool = False,  # noqa: FBT001, FBT002
    ) -> None:
        super().__init__(theme, default, debug)
        self._proc = None
        self.start_server()

    def __call__(self, *args, **kwargs) -> None:
        """
        Method called when an instance is called.
        """
        if self._proc is not None and self._proc.poll() is not None:
            msg = "Server has ended, please recreate your plot generator object."
            raise RuntimeError(msg)
        path = None
        if "path" in kwargs:
            path = kwargs["path"]
            del kwargs["path"]
        spec = self.get_spec(*args, **kwargs)
        res = ObsplotJsdom(
            spec,
            port=self._port,
            theme=self._theme,
            default=self._default,
            debug=self._debug,
        ).plot()
        if path is None:
            display(res)
        else:
            ObsplotJsdomCreator.save_to_file(path, res)

    def start_server(self):
        """
        Start http node plot generator server.
        """
        if self._proc is not None:
            if self._proc.poll() is None:
                # If proc already running, do nothing
                return
        # Check for node executable
        npx = shutil.which("npx")
        if not npx:
            msg = "npx executable has not been found."
            raise RuntimeError(msg)
        # Run node script with JSON spec as input
        try:
            p = Popen(
                ["npx", f"pyobsplot@{MIN_NPM_VERSION}"],  # noqa: S607
                stdin=None,
                stdout=PIPE,
                stderr=PIPE,
                encoding="Utf8",
                # Use shell=True if we are on Windows. Otherwise PATH
                # is not parsed and npx is not found.
                shell=os.name == "nt",  # noqa: S603
                start_new_session=True,
            )
        except SubprocessError:
            err = p.stderr.read()  # type: ignore
            msg = f"Can't start server: {err}"
            raise RuntimeError(msg) from SubprocessError
        # read back OS selected port from stdout
        try:
            port = p.stdout.readline()  # type: ignore
            self._port = int(port.strip())
        except ValueError:
            err = p.stderr.read()  # type: ignore
            msg = f"Server not started: {err}"
            raise ValueError(msg) from ValueError
        # store Popen process
        self._proc = p

    def close(self):
        """
        Stop http node plot generator server.
        """
        if self._proc is not None:
            os.killpg(os.getpgid(self._proc.pid), signal.SIGTERM)

    @staticmethod
    def save_to_file(path: str, res: Union[SVG, HTML]) -> None:
        """
        Save an Obsplot object generated by a Jsdom creator to a file.

        Args:
            path (str): path to output file.
            res (SVG | HTML): result of a call to Obsplot().

        Raises:
            RuntimeWarning: if the file extension doesn't match the Obsplot type.
        """
        if isinstance(path, io.StringIO):
            path.write(str(res.data))
            return
        extension = Path(path).suffix.lower()
        if extension not in [".html", ".svg", ".htm"]:
            warnings.warn(
                "Output file extension should be one of 'html' or 'svg'",
                RuntimeWarning,
                stacklevel=1,
            )
        if isinstance(res, HTML) and extension == ".svg":
            warnings.warn(
                f"Output is HTML but file extension is '{extension}'",
                RuntimeWarning,
                stacklevel=1,
            )
        with open(path, "w", encoding="utf-8") as f:
            f.write(str(res.data))
