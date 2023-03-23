import pathlib
import anywidget
import traitlets
from random import random

# bundler yields hello_widget/static/{index.js,styles.css}
bundler_output_dir = pathlib.Path("static")


class ObsPlot(anywidget.AnyWidget):
    _esm = bundler_output_dir / "index.js"
    _css = bundler_output_dir / "index.css"
    spec = traitlets.Dict().tag(sync=True)

    @traitlets.validate("spec")
    def _validate_spec(self, proposal):
        prop = proposal["value"]
        # if prop["length"] is None:
        #    raise traitlets.TraitError("Missing length")
        # prop["alea"] = random()
        return prop


class JSModule(type):
    def __getattr__(cls, name):
        def wrapper(*args, **kwargs):
            if kwargs:
                raise ValueError(
                    f"kwargs must not be passed to f{cls.__name__}.{name} : {kwargs}"
                )
            return {
                "ipyobsplot-type": "function",
                "module": cls.__name__,
                "method": name,
                "args": args,
            }

        return wrapper


class Plot(metaclass=JSModule):
    pass


class d3(metaclass=JSModule):
    pass


def js(str):
    pass
