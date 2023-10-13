from functools import partial
from typing import Callable, Optional

from pyobsplot.obsplot import ObsplotJsdomCreator, ObsplotWidgetCreator
from pyobsplot.utils import PLOT_METHODS
from pyobsplot.widget import ObsplotWidget

# Default renderer for Plot.plot() calls.
# Not documented, only internal use for documentation generation
_plot_renderer = "widget"


class Plot:
    """Plot methods class."""

    @staticmethod
    def plot(*args, **kwargs) -> Optional[ObsplotWidget]:
        """
        Plot.plot static method. If called directly, create an ObsplotWidget
        or an ObpsplotJsdom with args and kwargs.
        """
        op = None
        if _plot_renderer == "widget":
            op = ObsplotWidgetCreator()
        if _plot_renderer == "jsdom":
            op = ObsplotJsdomCreator()
        if op is not None:
            return op(*args, **kwargs)


def method_to_spec(*args, **kwargs) -> dict:
    """Function used for creating Plot.xyz static methods.
    Generates a dict of specification with method name and args.

    Returns:
        dict: Plot function specification.
    """
    name = kwargs["name"]
    if len(kwargs) > 1:
        msg = f"kwargs must not be passed to Plot.{name} : {kwargs}"
        raise ValueError(msg)
    return {
        "pyobsplot-type": "function",
        "module": "Plot",
        "method": name,
        "args": args,
    }


# For each exitsting JS Plot method, create a static Python Plot method with the
# same name which calls method_to_spec()
for method in PLOT_METHODS:
    if method != "plot":
        setattr(Plot, method, staticmethod(partial(method_to_spec, name=method)))


class JSModule(type):
    """metaclass to allow JavaScript module and methods handling."""

    def __getattr__(cls: type, name: str) -> Callable:
        """Intercept methods calling and returns a parsed and typed dict object."""

        def wrapper(*args, **kwargs) -> dict:
            if kwargs:
                msg = f"kwargs must not be passed to {cls.__name__}.{name} : {kwargs}"
                raise ValueError(msg)
            return {
                "pyobsplot-type": "function",
                "module": cls.__name__,
                "method": name,
                "args": args,
            }

        return wrapper


class d3(metaclass=JSModule):  # noqa: N801
    """JSModule class to allow d3 objects in specification."""

    pass


class Math(metaclass=JSModule):
    """JSModule class to allow Math objects in specification."""

    pass
