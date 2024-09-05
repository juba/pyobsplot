import importlib.metadata

from pyobsplot.js_modules import Math, d3
from pyobsplot.obsplot import Obsplot
from pyobsplot.parsing import js
from pyobsplot.plot import Plot

__version__ = importlib.metadata.version("pyobsplot")

__all__ = ["Obsplot", "Plot", "d3", "Math", "js"]
