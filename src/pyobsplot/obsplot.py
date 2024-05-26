"""
Obsplot main class.
"""

from __future__ import annotations

import io
import os
import shutil
import signal
import tempfile
import warnings
from pathlib import Path
from subprocess import PIPE, Popen, SubprocessError
from typing import Literal

import typst
from IPython.display import HTML, SVG, Image, display
from ipywidgets.embed import embed_minimal_html

from pyobsplot.jsdom import ObsplotJsdom
from pyobsplot.utils import (
    ALLOWED_DEFAULTS,
    ALLOWED_FORMAT_OPTIONS,
    AVAILABLE_THEMES,
    DEFAULT_THEME,
    MIN_NPM_VERSION,
    bundler_output_dir,
)
from pyobsplot.widget import ObsplotWidget

AVAILABLE_FORMATS = ["widget", "html", "svg", "png"]


class Obsplot:

    def __init__(
        self,
        format: Literal["widget", "html", "svg", "png"] = "widget",  # noqa: A002
        *,
        theme: Literal["light", "dark", "current"] = DEFAULT_THEME,
        default: dict | None = None,
        format_options: dict | None = None,
        debug: bool = False,
        renderer: str | None = None,
    ) -> None:
        """
        Main Obsplot class.

        Parameters
        ----------
        format : {'widget', 'html', 'svg', 'png'}, optional
            default output format, by default "widget"
        theme : {'light', 'dark', 'current'}, optional
            color theme to use, by default 'light'
        default : dict, optional
            dict of default spec values, by default None
        format_options : dict, optional
            default output format options for typst formatter. Currently
            possible keys are 'font' (name of font family), 'scale' (font scaling)
            and 'margin' (margin in pt around the plot)
        debug : bool, optional
            activate debug mode, by default False
        renderer : str, optional
            DEPRECATED, use `format` instead.
        """

        # Check for renderer value
        if renderer is not None:
            if renderer == "widget":
                msg = (
                    "The 'renderer' argument is deprecated.\n"
                    "Use format='widget' instead."
                )
                raise ValueError(msg)
            if renderer == "jsdom":
                msg = (
                    "The 'renderer' argument is deprecated.\n"
                    "Use format='html', format='svg' or format='png' instead."
                )
                raise ValueError(msg)
            else:
                msg = "The 'renderer' argument is deprecated. Use 'format' instead."
                raise ValueError(msg)

        # Check theme value
        if theme not in AVAILABLE_THEMES:
            msg = f"""
                Incorrect theme '{theme}'.
                Available themes are {AVAILABLE_THEMES}
                """
            raise ValueError(msg)

        # Check format value
        if format not in AVAILABLE_FORMATS:
            msg = (
                f"Incorrect format value '{format}'."
                f"Available formats are {AVAILABLE_FORMATS}."
            )
            raise ValueError(msg)

        # Check default value
        default = default or {}
        for k in default:
            if k not in ALLOWED_DEFAULTS:
                msg = f"{k} is not allowed in default.\nAllowed values: {ALLOWED_DEFAULTS}."  # noqa: E501
                raise ValueError(msg)

        # Check format options
        format_options = format_options or {}
        for k in format_options:
            if k not in ALLOWED_FORMAT_OPTIONS:
                msg = f"{k} is not allowed in format options.\nAllowed values: {ALLOWED_FORMAT_OPTIONS}."  # noqa: E501
                raise ValueError(msg)

        self.theme = theme
        self.default = default
        self.format = format
        self.format_options = format_options
        self.debug = debug

        self.widget_creator = None
        self.jsdom_creator = None

    def __repr__(self):
        return (
            f"<{type(self).__name__}>\n"
            f"format: {self.format!r}\n"
            f"theme: {self.theme!r}\n"
            f"default: {self.default!r}\n"
            f"format_options: {self.format_options!r}\n"
            f"debug: {self.debug!r}\n"
        )

    def __call__(
        self,
        spec: dict,
        format: Literal["widget", "html", "svg", "png"] | None = None,  # noqa: A002
        theme: Literal["light", "dark", "current"] | None = None,
        path: str | io.StringIO | None = None,
        format_options: dict | None = None,
    ) -> ObsplotWidget | None:
        """
        Method called when an Obsplot instance is called directly.

        Parameters
        ----------
        spec : dict
            plot specification
        format : {'widget', 'html', 'svg', 'png'}, optional
            default output format, by default "widget"
        theme : {'light', 'dark', 'current'}, optional
            color theme to use, by default 'light'
        path : str | io.StringIO | None, optional
            if provided, plot is saved to disk to an HTML file instead of displayed
            as a jupyter widget, by default None
        format_options : dict, optional
            default output format options for typst formatter. Currently
            possible keys are 'font' (name of font family), 'scale' (font scaling)
            and 'margin' (margin in pt around the plot)
        """

        format_value = format or self.format
        format_options = format_options or self.format_options
        theme = theme or self.theme  # type: ignore
        default = self.default
        debug = self.debug

        # Check spec
        if not isinstance(spec, dict):
            msg = "Plot specification should be given as a dictionary."
            raise ValueError(msg)

        # Check path value and update format_value based on extension
        if path is not None and not isinstance(path, io.StringIO):
            extension = Path(path).suffix.lower()[1:]
            allowed_extensions = ["html", "svg", "pdf", "png"]
            if extension not in allowed_extensions:
                msg = f"Output file extension should be one of {allowed_extensions}"
                raise ValueError(msg)
            if format_value == "widget" and extension != "html":
                msg = "File extension should be 'html' when exporting a widget."
                raise ValueError(msg)
            if format_value not in ["widget", extension]:
                warnings.warn(
                    f"Generating file in {extension} format based on file extension.",
                    RuntimeWarning,
                    stacklevel=1,
                )
            format_value = extension

        # Render widget
        if format_value == "widget":
            res = ObsplotWidget(
                spec=spec, theme=theme, default=default, debug=debug  # type: ignore
            )  # type: ignore
            if path is not None:
                embed_minimal_html(path, views=[res], drop_defaults=False)
            else:
                return res

        # Render jsdom
        if format_value != "widget":
            self._jsdom_start()
            self.jsdom_creator.render(  # type: ignore
                spec=spec,
                format=format_value,  # type: ignore
                format_options=format_options,
                theme=theme,  # type: ignore
                default=default,
                debug=debug,
                path=path,
            )

    def _jsdom_start(self):
        """
        Start the JsdomCreator server.
        """
        if self.jsdom_creator is None:
            self.jsdom_creator = ObsplotJsdomCreator()

    def _jsdom_close(self):
        """
        Stop the JsdomCreator server.
        """
        if self.jsdom_creator is not None:
            self.jsdom_creator.close()


class ObsplotJsdomCreator:

    def __init__(
        self,
    ) -> None:
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

    def render(
        self,
        spec: dict,
        *,
        format: Literal["widget", "html", "svg", "png"] = "widget",  # noqa: A002
        theme: Literal["light", "dark", "current"] = DEFAULT_THEME,
        path: str | io.StringIO | None = None,
        format_options: dict | None = None,
        default: dict | None = None,
        debug: bool = False,
    ) -> None:
        """
        Method called when an instance is called.

        Parameters
        ----------
        spec : dict
            plot specification
        format : {'widget', 'html', 'svg', 'png'}, optional
            default output format, by default "widget"
        theme : {'light', 'dark', 'current'}, optional
            color theme to use, by default 'light'
        path : str | io.StringIO | None, optional
            if provided, plot is saved to disk to an HTML file instead of displayed
            as a jupyter widget, by default None
        format_options : dict, optional
            default output format options for typst formatter. Currently
            possible keys are 'font' (name of font family), 'scale' (font scaling)
            and 'margin' (margin in pt around the plot)
        default : dict, optional
            dict of default spec values, by default None
        debug : bool, optional
            activate debug mode, by default False
        """
        if self._proc is not None and self._proc.poll() is not None:
            msg = "Server has ended, please recreate your plot generator object."
            raise RuntimeError(msg)

        force_figure = "figure" not in spec and format in ["html", "png", "pdf"]

        res = ObsplotJsdom(
            spec=spec,
            port=self._port,
            theme=theme,
            default=default,
            debug=debug,
            force_figure=force_figure,
        ).plot()

        if format in ["png", "pdf"] or format == "svg" and isinstance(res, HTML):
            if format == "svg" and isinstance(res, HTML):
                warnings.warn(
                    "HTML figure converted to SVG via typst.",
                    RuntimeWarning,
                    stacklevel=1,
                )
            res = self.typst_render(res, format, format_options)  # type: ignore

        if path is None:
            display(res)
        else:
            ObsplotJsdomCreator.save_to_file(path, res)  # type: ignore

    def typst_render(
        self,
        figure: HTML,
        format: Literal["pdf", "svg", "png"],  # noqa: A002
        options: dict | None = None,
    ) -> SVG | Image | bytes:
        """
        Run an HTML jsdom output through typst for conversion to png, pdf or svg.

        Parameters
        ----------
        figure : HTML
            output of jsdom renderer (HTML)
        format : {'png', 'pdf', 'svg'}
            format of output to generate.
        options : dict, optional
            dictionary of format options.

        Returns
        -------
        SVG | Image | bytes
            Conversion result.

        """

        if options is None:
            options = {}

        if format not in ["png", "pdf", "svg"]:
            msg = f"Invalid format: {format}."
            raise ValueError(msg)

        with tempfile.TemporaryDirectory() as tmpdirname:
            tmpdir = Path(tmpdirname)
            input_file = tmpdir / "input.typ"
            output_file = tmpdir / f"out.{format}"

            # Write HTML jsdom output to file
            with open(tmpdir / "jsdom.html", "w") as jsdom_out:
                jsdom_out.write(str(figure.data))
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
    def save_to_file(path: str, res: SVG | HTML | Image) -> None:
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
