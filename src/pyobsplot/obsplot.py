"""
Obsplot main class.
"""

import shutil
import os
import signal
from subprocess import Popen, PIPE, SubprocessError
from IPython.display import display
from typing import Any

from .widget import ObsplotWidget
from .jsdom import ObsplotJsdom
from .utils import allowed_defaults, min_npm_version


class Obsplot:
    """
    Main Obsplot class.

    Launches a Jupyter widget with ObsplotWidget class, or displays an IPython display
    with ObsplotJsdom depending on the renderer.
    """

    def __new__(
        cls, renderer: str = "widget", default: dict = {}, debug: bool = False
    ) -> Any:
        """
        Main Obsplot class constructor. Returns a Creator instance depending on the
        renderer passed as argument.

        Args:
            renderer (str): renderer to be used.
            default (dict): dict of default spec values.
            debug (bool): if True, activate debug mode (for widget renderer only)

        returns:
            A Creator object of type depending of the renderer.
        """

        available_renderers = ["widget", "jsdom"]

        # Plot spec with the configured renderer
        if renderer == "widget":
            return ObsplotWidgetCreator(default=default, debug=debug)
        elif renderer == "jsdom":
            return ObsplotJsdomCreator(default=default, debug=debug)
        else:
            raise ValueError(
                f"""
                Incorrect renderer '{renderer}'. 
                Available renderers are {available_renderers}
                """
            )


class ObsplotCreator:
    """
    Creator class.
    """

    def __init__(self, default: dict = {}, debug: bool = False) -> None:
        """Generic Creator constructor

        Args:
            default (dict, optional): dict of default spec values. Defaults to {}.
        """
        for k in default:
            if k not in allowed_defaults:
                raise ValueError(
                    f"{k} is not allowed in default.\nAllowed values: {allowed_defaults}."  # noqa: E501
                )
        self._default = default
        self._debug = debug

    def __repr__(self):
        return (
            f"<{type(self).__name__}>\n"
            f"debug: {self._debug!r}\n"
            f"default: {self._default!r}\n"
        )

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
            raise ValueError("Missing plot specification")
        else:
            raise ValueError("Incorrect plot specification")
        return spec


class ObsplotWidgetCreator(ObsplotCreator):
    """
    Widget renderer Creator class.
    """

    def __init__(self, default: dict = {}, debug: bool = False) -> None:
        super().__init__(default, debug)

    def __call__(self, *args, **kwargs) -> ObsplotWidget:
        """
        Method called when an instance is called.
        """
        spec = self.get_spec(*args, **kwargs)
        return ObsplotWidget(spec, default=self._default, debug=self._debug)


class ObsplotJsdomCreator(ObsplotCreator):
    """
    Jsdom renderer Creator class.
    """

    def __init__(self, default: dict = {}, debug: bool = False) -> None:
        super().__init__(default, debug)
        self._proc = None
        self.start_server()

    def __call__(self, *args, **kwargs) -> None:
        """
        Method called when an instance is called.
        """
        if self._proc.poll() is not None:
            raise RuntimeError(
                "Server has ended, please recreate your plot generator object."
            )
        spec = self.get_spec(*args, **kwargs)
        display(
            ObsplotJsdom(
                spec,
                port=self._port,
                default=self._default,
                debug=self._debug,
            ).plot()
        )

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
            raise RuntimeError("npx executable has not been found.")
        # Run node script with JSON spec as input
        try:
            p = Popen(
                ["npx", f"pyobsplot@{min_npm_version}"],
                stdin=None,
                stdout=PIPE,
                stderr=PIPE,
                encoding="Utf8",
                # Use shell=True if we are on Windows. Otherwise PATH
                # is not parsed and npx is not found.
                shell=os.name == "nt",
                start_new_session=True,
            )
        except SubprocessError:
            err = p.stderr.read()
            raise RuntimeError(f"Can't start server: {err}")
        # read back OS selected port from stdout
        try:
            port = p.stdout.readline()
            self._port = int(port.strip())
        except ValueError:
            err = p.stderr.read()
            raise ValueError(f"Server not started: {err}")
        # store Popen process
        self._proc = p

    def close(self):
        """
        Stop http node plot generator server.
        """
        os.killpg(os.getpgid(self._proc.pid), signal.SIGTERM)
