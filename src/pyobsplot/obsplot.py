"""
Obsplot main class.
"""

from IPython.display import display

from .widget import ObsplotWidget
from .jsdom import ObsplotJsdom


class Obsplot:
    renderer = "widget"

    @staticmethod
    def set_renderer(renderer):
        if renderer not in ["widget", "jsdom"]:
            raise ValueError("Incorrect renderer.")
        Obsplot.renderer = renderer

    def __new__(cls, *args, **kwargs):
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
