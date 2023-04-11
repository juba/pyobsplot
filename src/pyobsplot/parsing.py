"""
Plot specification parsing.
"""

import datetime
import json
import pandas as pd
import polars as pl

from typing import Any, Optional

from .data import serialize


class SpecParser:
    """
    Class implementing plot specification parsing.
    """

    def __init__(self, renderer: str = "widget", default: dict = {}) -> None:
        """
        SpecParser constructor.

        Args:
            renderer(str): type of renderer ("widget" or "jsdom").
            default(dict): dict of default spec values.
        """
        self.renderer = renderer
        self.data = []
        self._spec = dict()
        self._default = default

    @property
    def spec(self):
        return self._spec

    @spec.setter
    def spec(self, value):
        if (
            "pyobsplot-type" in value
            and value["pyobsplot-type"] == "function"
            and value["module"] == "Plot"
        ):
            value = {"marks": [value]}
        self._spec = value

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

    def merge_default(self, spec: dict) -> dict:
        """Merge SpecParser default spec values with an actual spec.

        Args:
            spec (dict): spec to update with default values.

        Returns:
            dict: merged spec.
        """
        default = self._default
        for k in default:
            if k not in spec:
                spec[k] = default[k]
        return spec

    def parse_spec(self) -> dict:
        """Start spec parsing from _spec attribute.

        Args:
            default (dict): default spec values defined during Creator creation.

        Returns:
            dict: parsed specification.
        """
        # Deep copy should not be needed and copy should be sufficient as
        # merge_default only affects top-level elements.
        spec = self.spec.copy()
        spec = self.merge_default(spec)
        return self.parse(spec)

    def parse(self, spec: Any) -> Any:
        """Recursively parse part of a Plot specification to check and convert
        its elements.

        Args:
            spec (Any): part of a specification.

        Returns:
            Any: parsed part of a specification.
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
        # If range, convert  to list
        if isinstance(spec, range):
            return self.parse(list(spec))
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
        return [serialize(d, renderer=self.renderer) for d in self.data]


def js(txt: str) -> dict:
    """Tag a string as JavaScript code.

    Args:
        txt (str): string containing JavaScript code.

    Returns:
        dict: tagged string as dict with type value.
    """
    return {"pyobsplot-type": "js", "value": txt}
