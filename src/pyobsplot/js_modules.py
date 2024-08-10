import io
from functools import partial
from pathlib import Path
from typing import Callable, Literal

from pyobsplot.obsplot import Obsplot
from pyobsplot.utils import PLOT_METHODS
from pyobsplot.widget import ObsplotWidget

# Default format for Plot.plot() calls.
# Not documented, only internal use for documentation generation
_plot_format = None


class Plot:
    """
    Plot methods class.
    """

    @staticmethod
    def plot(
        spec: dict,
        format: Literal["widget", "html", "svg", "png"] | None = None,  # noqa: A002
        path: str | None = None,
        format_options: dict | None = None,
    ) -> ObsplotWidget | None:
        """
        Plot.plot static method. If called directly, create an ObsplotWidget
        or an ObpsplotJsdom with args and kwargs.

        Parameters
        ----------
        spec : dict
            plot specification dictionary
        format : {'widget', 'html', 'svg', 'png'}, optional
            default output format, by default "widget"
        path : str | io.StringIO | None, optional
            if provided, plot is saved to disk to an HTML file instead of displayed
            as a jupyter widget, by default None
        format_options : dict, optional
            default output format options for typst formatter. Currently
            possible keys are 'font' (name of font family), 'scale' (font scaling)
            and 'margin' (margin around the plot, e.g. '1in' or '10pt')
        """
        format_value = format or _plot_format
        op = Obsplot(format=format_value, format_options=format_options)  # type: ignore
        return op(spec, path=path)


def method_to_spec(*args, **kwargs) -> dict:
    """
    Function used for creating Plot.xyz static methods.
    Generates a dict of specification with method name and args.

    Returns
    -------
    dict
        Plot function specification.
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
    """
    Metaclass to allow JavaScript module and methods handling.
    """

    def __getattr__(cls: type, name: str) -> Callable:
        """
        Intercept methods calling and returns a parsed and typed dict object.
        """

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
    """
    JSModule class to allow d3 objects in specification.
    """

    pass


class Math(metaclass=JSModule):
    """
    JSModule class to allow Math objects in specification.
    """

    pass
