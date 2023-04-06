from .obsplot import ObsplotWidgetCreator
from .widget import ObsplotWidget


class JSModule(type):
    """metaclass to allow JavaScript module and methods handling."""

    def __getattr__(cls: type, name: str) -> callable:
        """Intercept methods calling and returns a parsed and typed dict object."""

        # If "Plot.plot" is called, returns it as is.
        # This is to allow users to use `Plot.plot` directly to generate charts
        # without having to call Plot.plot = Obsplot() first.
        if ("pyobsplot.parsing", "Plot", "plot") == (
            cls.__module__,
            cls.__name__,
            name,
        ):
            return Plot.plot

        def wrapper(*args, **kwargs) -> dict:
            if kwargs:
                raise ValueError(
                    f"kwargs must not be passed to {cls.__name__}.{name} : {kwargs}"
                )
            return {
                "pyobsplot-type": "function",
                "module": cls.__name__,
                "method": name,
                "args": args,
            }

        return wrapper


class Plot(metaclass=JSModule):
    """JSModule class to allow Plot objects in specification."""

    @staticmethod
    def plot(*args, **kwargs) -> ObsplotWidget:
        """
        Plot.plot static method. If called directly, create an ObsplotWidget
        with args and kwargs.
        """
        op = ObsplotWidgetCreator()
        return op(*args, **kwargs)


class d3(metaclass=JSModule):
    """JSModule class to allow d3 objects in specification."""

    pass


class Math(metaclass=JSModule):
    """JSModule class to allow Math objects in specification."""

    pass
