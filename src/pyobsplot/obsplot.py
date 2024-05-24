"""
Obsplot main class.
"""

import io
import os
import shutil
import signal
import tempfile
import warnings
from pathlib import Path
from subprocess import PIPE, Popen, SubprocessError
from typing import Any, Optional, Union

import typst
from IPython.display import HTML, SVG, Image, display
from ipywidgets.embed import embed_minimal_html

from pyobsplot.jsdom import ObsplotJsdom
from pyobsplot.utils import (
    ALLOWED_DEFAULTS,
    AVAILABLE_THEMES,
    DEFAULT_THEME,
    MIN_NPM_VERSION,
    bundler_output_dir,
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
        *,
        theme: str = DEFAULT_THEME,
        default: Optional[dict] = None,
        format: Optional[str] = None,  # noqa: A002
        format_options: Optional[dict] = None,
        debug: bool = False,
    ) -> Any:
        """
        Main Obsplot class constructor. Returns a Creator instance depending on the
        renderer passed as argument.

        Args:
            renderer (str): renderer to be used.
            theme (str): color theme to use, can be "light" (default), "dark" or
                "current".
            default (dict): dict of default spec values.
            format (str): default output display format for jsdom renderer, can be
                "html", "svg", "png" or "pdf".
            format_options (dict): default options passed to typst when converting
                to png or pdf.
            debug (bool): if True, activate debug mode (for widget renderer only)

        returns:
            A Creator object of type depending of the renderer.
        """

        # Check theme value
        if theme not in AVAILABLE_THEMES:
            msg = f"""
                Incorrect theme '{theme}'.
                Available themes are {AVAILABLE_THEMES}
                """
            raise ValueError(msg)

        # Check renderer value
        available_renderers = ["widget", "jsdom"]
        if renderer not in available_renderers:
            msg = (
                f"Incorrect renderer '{renderer}'."
                f"Available renderers are {available_renderers}."
            )
            raise ValueError(msg)

        # Generate and return creator object
        if renderer == "widget":
            if format is not None:
                msg = (
                    "The format option is incompatible with the widget renderer."
                    "Use the jsdom renderer instead."
                )
                raise ValueError(msg)
            return ObsplotWidgetCreator(theme=theme, default=default, debug=debug)

        elif renderer == "jsdom":
            if format_options is None:
                format_options = {}
            return ObsplotJsdomCreator(
                theme=theme,
                default=default,
                debug=debug,
                format=format,
                format_options=format_options,
            )


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
        *,
        theme: str = DEFAULT_THEME,
        default: Optional[dict] = None,
        format: Optional[str] = None,  # noqa: A002
        format_options: Optional[dict] = None,
        debug: bool = False,
    ) -> None:

        super().__init__(theme, default, debug)

        allowed_formats = ["html", "svg", "png"]
        if format is not None and format not in allowed_formats:
            msg = (
                f"Incorrect format '{format}'. "
                f"Available formats are '{allowed_formats}'."
            )
            raise ValueError(msg)

        self.format = format
        if format_options is None:
            format_options = {}
        self.format_options = format_options
        self._proc = None
        self.start_server()

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

    def __call__(
        self,
        *args,
        **kwargs,
    ) -> None:
        """
        Method called when an instance is called.
        """
        if self._proc is not None and self._proc.poll() is not None:
            msg = "Server has ended, please recreate your plot generator object."
            raise RuntimeError(msg)

        # Extract configuration arguments from spec
        path = None
        if "path" in kwargs:
            path = kwargs["path"]
            del kwargs["path"]
        if "format" in kwargs:
            format = kwargs["format"]  # noqa: A001
            del kwargs["format"]
        else:
            format = self.format  # noqa: A001
        if "format_options" in kwargs:
            format_options = kwargs["format_options"]
            del kwargs["format_options"]
        else:
            format_options = self.format_options

        allowed_formats = ["html", "png", "svg"]
        if format is not None and format not in allowed_formats:
            msg = f"Invalid format: {format}.\n Allowed formats: {allowed_formats}."
            raise ValueError(msg)

        if path is not None and not isinstance(path, io.StringIO):
            extension = Path(path).suffix.lower()[1:]
            allowed_extensions = ["html", "svg", "pdf", "png"]
            if extension not in allowed_extensions:
                msg = f"Output file extension should be one of {allowed_extensions}"
                raise ValueError(msg)
            # If both format and path are provided, use path extension
            if format is not None and format != extension:
                warnings.warn(
                    f"Generating file in {extension} format based on file extension.",
                    RuntimeWarning,
                    stacklevel=1,
                )
            format = extension  # noqa: A001

        spec = self.get_spec(*args, **kwargs)
        if "figure" not in spec and format in ["html", "png", "pdf"]:
            spec["figure"] = True

        res = ObsplotJsdom(
            spec,
            port=self._port,
            theme=self._theme,
            default=self._default,
            debug=self._debug,
        ).plot()

        if format in ["png", "pdf"] or format == "svg" and isinstance(res, HTML):
            if format == "svg" and isinstance(res, HTML):
                warnings.warn(
                    f"HTML figure converted to SVG via typst.",
                    RuntimeWarning,
                    stacklevel=1,
                )
            res = self.typst_render(res, format, format_options)

        if path is None:
            display(res)
        else:
            ObsplotJsdomCreator.save_to_file(path, res)  # type: ignore

    def typst_render(self, res, format, options) -> SVG | Image | bytes:  # noqa: A002

        if format not in ["png", "pdf", "svg"]:
            msg = f"Invalid format: {format}."
            raise ValueError(msg)

        with tempfile.TemporaryDirectory() as tmpdirname:
            tmpdir = Path(tmpdirname)
            input_file = tmpdir / "input.typ"
            output_file = tmpdir / f"out.{format}"

            # Write HTML jsdom output to file
            with open(tmpdir / "jsdom.html", "w") as jsdom_out:
                jsdom_out.write(res.data)
            # Copy typst template
            shutil.copy(bundler_output_dir / "template.typ", tmpdir / "template.typ")
            # Create the typst input file
            with open(input_file, "w") as typst_file:
                typst_content = (
                    '#import "template.typ": obsplot\n#show: obsplot("jsdom.html",'
                )
                if "margin" in options:
                    value = options["margin"]
                    typst_content += f"margin: {value}pt,"
                if "font" in options:
                    value = options["font"]
                    typst_content += f'font-family: "{value}",'
                if "scale" in options:
                    value = options["scale"]
                    typst_content += f"scale: {value},"
                typst_content += ")"
                typst_file.write(typst_content)

            typst.compile(input_file, output=output_file, ppi=100, format=format)

            mode = "rb" if format in ["png", "pdf"] else "r"
            with open(output_file, mode) as f:
                res = f.read()
            if format == "png":
                res = Image(res)
            if format == "svg":
                res = SVG(res)

        return res

    @staticmethod
    def save_to_file(path: str, res: Union[SVG, HTML, Image]) -> None:
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
        if isinstance(res, Image):
            with open(path, "wb") as f:
                f.write(res.data)  # type: ignore
        if isinstance(res, bytes):
            with open(path, "wb") as f:
                f.write(res)  # type: ignore
        if isinstance(res, (HTML, SVG)):
            with open(path, "w", encoding="utf-8") as f:
                f.write(str(res.data))
