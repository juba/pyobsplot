"""
Plot specification parsing.
"""

import datetime
import json
import base64
import pandas as pd
import polars as pl

from typing import Any, Optional

from .data import pd_to_arrow, pl_to_arrow


class SpecParser:
    """
    Class implementing plot specification parsing.
    """

    def __init__(self, renderer: str = "widget") -> None:
        """
        SpecParser constructor.

        Args:
            renderer(str): type of renderer ("widget" or "jsdom").
        """
        self.renderer = renderer
        self.data = []

    def cache_index(self, data: Any) -> Optional[int]:
        """Returns the index of a data object in the data cache.

        Args:
            data (Any): a data object (DataFeame, GeoJson...)

        Returns:
            Optional[int]: index of the data object in the cache, or None if absent.
        """
        index = [i for i, d in enumerate(self.data) if d is data]
        if len(index) == 1:
            return index[0]
        return None

    def parse(self, spec: Any) -> Any:
        """Recursively parse a Plot specification to check and convert its elements.

        Args:
            spec (Any): a complete specification or part of a specification.

        Returns:
            Any: parsed specification or part of a specification.
        """
        if spec is None:
            return None
        # If list or tuple, recursively parse elements
        if isinstance(spec, (list, tuple)):
            return [self.parse(s) for s in spec]
        # If Geojson as string, parse as dict and continue parsing
        if isinstance(spec, str) and spec[0:28] == '{"type": "FeatureCollection"':
            spec = json.loads(spec)
        # If Geojson as dict, handle caching, don't parse, add type and returns as is
        if (
            isinstance(spec, dict)
            and "type" in spec
            and spec["type"] == "FeatureCollection"
        ):
            index = self.cache_index(spec)
            if index is None:
                self.data.append(spec)
                return {"pyobsplot-type": "GeoJson-ref", "value": (len(self.data) - 1)}
            else:
                return {"pyobsplot-type": "GeoJson-ref", "value": index}
        # If dict, parse recursively
        if isinstance(spec, dict):
            return {k: self.parse(v) for k, v in spec.items()}
        # If pandas DataFrame, handle caching, add type and serialize to Arrow IPC
        if isinstance(spec, pd.DataFrame):
            index = self.cache_index(spec)
            if index is None:
                self.data.append(spec)
                return {
                    "pyobsplot-type": "DataFrame-ref",
                    "value": (len(self.data) - 1),
                }
            else:
                return {"pyobsplot-type": "DataFrame-ref", "value": index}
        # If polars DataFrame, handle caching, add type and serialize to Arrow IPC
        if isinstance(spec, pl.DataFrame):
            index = self.cache_index(spec)
            if index is None:
                self.data.append(spec)
                return {
                    "pyobsplot-type": "DataFrame-ref",
                    "value": (len(self.data) - 1),
                }
            else:
                return {"pyobsplot-type": "DataFrame-ref", "value": index}
        # If pandas Series, convert to DataFrame and parse
        if isinstance(spec, pd.Series):
            return self.parse(pd.DataFrame(spec))
        # If polars Series, convert to DataFrame and parse
        if isinstance(spec, pl.Series):
            return self.parse(pl.DataFrame(spec))
        # If date or datetime, add tupe and convert to isoformat.
        if isinstance(spec, datetime.date) or isinstance(spec, datetime.datetime):
            return {"pyobsplot-type": "datetime", "value": spec.isoformat()}
        # Handling of JavaScript methods as objects, such as "Math.sin"
        # Manually call the parsed result ans add a special "function-object" type
        if (
            callable(spec)
            and isinstance(spec(), dict)
            and spec()["pyobsplot-type"] == "function"
        ):
            out = spec()
            out["pyobsplot-type"] = "function-object"
            return out
        return spec

    def serialize_data(self) -> list:
        """Serialize data in the data cache.

        Returns:
            list: list of serialized data objects.
        """
        result = []
        for d in self.data:
            # If polars DataFrame, serialize to Arrow IPC
            if isinstance(d, pl.DataFrame):
                value = pl_to_arrow(d)
                if self.renderer == "jsdom":
                    value = base64.standard_b64encode(value).decode("ascii")
                result.append({"pyobsplot-type": "DataFrame", "value": value})
            # If pandas DataFrame, serialize to Arrow IPC
            elif isinstance(d, pd.DataFrame):
                value = pd_to_arrow(d)
                if self.renderer == "jsdom":
                    value = base64.standard_b64encode(value).decode("ascii")
                result.append({"pyobsplot-type": "DataFrame", "value": value})
            # Else, keep as is
            else:
                result.append(d)
        return result


def js(txt: str) -> dict:
    """Tag a string as JavaScript code.

    Args:
        txt (str): string containing JavaScript code.

    Returns:
        dict: tagged string as dict with type value.
    """
    return {"pyobsplot-type": "js", "value": txt}
