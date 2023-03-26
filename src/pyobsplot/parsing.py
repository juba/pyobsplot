import datetime
import pandas as pd
import polars as pl

from .data import pd_to_arrow, pl_to_arrow

def parse_spec(spec):
    if spec is None:
        return None
    if isinstance(spec, list) or isinstance(spec, tuple):
        return [parse_spec(s) for s in spec]
    if (
        isinstance(spec, dict)
        and "type" in spec
        and spec["type"] == "FeatureCollection"
    ):
        return {"pyobsplot-type": "GeoJson", "value": spec}
    if isinstance(spec, dict):
        return {k: parse_spec(v) for k, v in spec.items()}
    if isinstance(spec, pd.DataFrame):
        return {"pyobsplot-type": "DataFrame", "value": pd_to_arrow(spec)}
    if isinstance(spec, pl.DataFrame):
        return {"pyobsplot-type": "DataFrame", "value": pl_to_arrow(spec)}
    if isinstance(spec, datetime.date) or isinstance(spec, datetime.datetime):
        return {"pyobsplot-type": "datetime", "value": spec.isoformat()}
    if (
        callable(spec)
        and isinstance(spec(), dict)
        and spec()["pyobsplot-type"] == "function"
    ):
        out = spec()
        out["pyobsplot-type"] = "function-object"
        return out
    return spec


class JSModule(type):
    def __getattr__(cls, name):
        def wrapper(*args, **kwargs):
            if kwargs:
                raise ValueError(
                    f"kwargs must not be passed to f{cls.__name__}.{name} : {kwargs}"
                )
            return {
                "pyobsplot-type": "function",
                "module": cls.__name__,
                "method": name,
                "args": args,
            }

        return wrapper


class Plot(metaclass=JSModule):
    pass


class d3(metaclass=JSModule):
    pass


class Math(metaclass=JSModule):
    pass


def js(txt):
    return {"pyobsplot-type": "js", "value": txt}
