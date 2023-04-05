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

    def __new__(cls, renderer: str = "widget", *args, **kwargs) -> Any:
        """
        Main Obsplot class constructor. Returns a Creator instance depending on the
        renderer passed as argument.
        """

        available_renderers = ["widget", "jsdom"]

        # Plot spec with the configured renderer
        if renderer == "widget":
            return ObsplotWidgetCreator(*args, **kwargs)
        elif renderer == "jsdom":
            return ObsplotJsdomCreator(*args, **kwargs)
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
        else:
            raise ValueError("Incorrect ObsPlot arguments")
        return spec


class ObsplotWidgetCreator(ObsplotCreator):
    """
    Widget renderer Creator class.
    """

    def __init__(self, *args, **kwargs) -> None:
        pass

    def __call__(self, *args, **kwargs):
        """
        Method called whent an instance is called.
        """
        spec = self.get_spec(*args, **kwargs)
        return ObsplotWidget(spec)


class ObsplotJsdomCreator(ObsplotCreator):
    """
    Jsdom renderer Creator class.
    """

    def __init___(self, *args, **kwargs) -> None:
        pass

    def __call__(self, *args, **kwargs):
        """
        Method called whent an instance is called.
        """
        spec = self.get_spec(*args, **kwargs)
        display(ObsplotJsdom(spec).plot())
