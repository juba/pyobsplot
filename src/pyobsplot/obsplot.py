"""
Obsplot main class.
"""

from IPython.display import display

from .widget import ObsplotWidget
from .jsdom import ObsplotJsdom
from .utils import default_renderer, available_renderers


class Obsplot:
    """
    Main Obsplot class.

    Launches a Jupyter widget with ObsplotWidget class, or displays an IPython display
    with ObsplotJsdom depending on the renderer.
    """

    # Default renderer
    renderer = default_renderer

    @staticmethod
    def set_renderer(renderer: str) -> None:
        """Set the renderer for next Obsplot calls.

        Args:
            renderer (str): renderer name.

        """
        if renderer not in available_renderers:
            raise ValueError(
                f"Incorrect renderer. Must be one of {available_renderers}."
            )
        Obsplot.renderer = renderer

    def __new__(cls, *args, **kwargs) -> None:
        """
        Constructor. Extract spec from args and kwargs, and call the configured renderer.
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

        # Plot spec with the configured renderer
        if Obsplot.renderer == "widget":
            return ObsplotWidget(spec)
        elif Obsplot.renderer == "jsdom":
            display(ObsplotJsdom(spec).plot())
        else:
            raise ValueError("Incorrect renderer.")
