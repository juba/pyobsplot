"""
Obsplot main class.
"""

from IPython.display import display
from typing import Any

from .widget import ObsplotWidget
from .jsdom import ObsplotJsdom


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
            if debug:
                raise ValueError("debug mode is not available with jsdom renderer")
            return ObsplotJsdomCreator(default=default)
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

    def __init__(self, default: dict = {}) -> None:
        allowed_default = [
            "marginTop",
            "marginRight",
            "marginBottom",
            "marginLeft",
            "margin",
            "width",
            "height",
            "aspectRatio",
            "style",
        ]
        for k in default:
            if k not in allowed_default:
                raise ValueError(
                    f"{k} is not allowed in default.\nAllowed values: {allowed_default}."  # noqa: E501
                )
        self._default = default

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
        super().__init__(default)
        self._debug = debug

    def __call__(self, *args, **kwargs) -> ObsplotWidget:
        """
        Method called whent an instance is called.
        """
        spec = self.get_spec(*args, **kwargs)
        return ObsplotWidget(spec, default=self._default, debug=self._debug)


class ObsplotJsdomCreator(ObsplotCreator):
    """
    Jsdom renderer Creator class.
    """

    def __init__(self, default: dict = {}) -> None:
        super().__init__(default)

    def __call__(self, *args, **kwargs) -> None:
        """
        Method called whent an instance is called.
        """
        spec = self.get_spec(*args, **kwargs)
        display(ObsplotJsdom(spec, default=self._default).plot())
