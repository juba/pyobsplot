"""
Obsplot main class.
"""

from .widget import ObsplotWidget
from IPython.display import HTML
import subprocess


class Obsplot:
    renderer = "widget"

    @staticmethod
    def set_renderer(renderer):
        if renderer not in ["widget", "jsdom"]:
            raise ValueError("Incorrect renderer.")
        Obsplot.renderer = renderer

    def __new__(cls, *args, **kwargs):
        if Obsplot.renderer == "widget":
            return ObsplotWidget(*args, **kwargs)
        elif Obsplot.renderer == "jsdom":
            raise NotImplementedError("Not implemented.")
        else:
            raise ValueError("Incorrect renderer.")
