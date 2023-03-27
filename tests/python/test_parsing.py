"""
Tests for specification parsing.
"""

import pytest

import pandas as pd
import polars as pl
import datetime

from pyobsplot import parsing
from pyobsplot.parsing import parse_spec, js
from pyobsplot.data import pd_to_arrow, pl_to_arrow


class TestParseSpec:
    def test_parse_spec_none(self):
        assert parse_spec(None) is None

    def test_parse_spec_recursive(self):
        assert parse_spec([1, "foo", None]) == [1, "foo", None]
        assert parse_spec((1, "foo", None)) == [1, "foo", None]
        assert parse_spec({"x": 1, "y": "foo", "z": None}) == {
            "x": 1,
            "y": "foo",
            "z": None,
        }

    def test_parse_spec_geojson(self):
        df = pd.DataFrame({"x": [1, 2], "y": [1, 3]})
        assert parse_spec({"type": "FeatureCollection", "val": df}) == {
            "pyobsplot-type": "GeoJson",
            "value": {
                "type": "FeatureCollection",
                "val": df,
            },
        }

    def test_parse_spec_dataframe(self):
        df_pd = pd.DataFrame({"x": [1, 2], "y": ["foo", "bar"]})
        df_pl = pl.DataFrame({"x": [1, 2], "y": ["foo", "bar"]})
        assert parse_spec(df_pd) == {
            "pyobsplot-type": "DataFrame",
            "value": pd_to_arrow(df_pd),
        }
        assert parse_spec(df_pl) == {
            "pyobsplot-type": "DataFrame",
            "value": pl_to_arrow(df_pl),
        }

    def test_parse_spec_series(self):
        df_pd = pd.DataFrame({"x": [1, 2], "y": ["foo", "bar"]})
        series_pd = df_pd["x"]
        df_pl = pl.DataFrame({"x": [1, 2], "y": ["foo", "bar"]})
        series_pl = df_pl.get_column("x")
        assert parse_spec(series_pd) == {
            "pyobsplot-type": "DataFrame",
            "value": pd_to_arrow(pd.DataFrame(df_pd["x"])),
        }
        assert parse_spec(series_pl) == {
            "pyobsplot-type": "DataFrame",
            "value": pl_to_arrow(pl.DataFrame(df_pl.get_column("x"))),
        }

    def test_parse_spec_datetime(self):
        assert parse_spec(datetime.date(2023, 1, 1)) == {
            "pyobsplot-type": "datetime",
            "value": "2023-01-01",
        }
        assert parse_spec(datetime.datetime(2023, 1, 1, 14, 25, 12)) == {
            "pyobsplot-type": "datetime",
            "value": "2023-01-01T14:25:12",
        }

    def test_parse_spec_js(self):
        assert parse_spec(parsing.Plot.foo()) == {
            "pyobsplot-type": "function",
            "module": "Plot",
            "method": "foo",
            "args": [],
        }
        assert parse_spec(parsing.d3.bar(1, "baz")) == {
            "pyobsplot-type": "function",
            "module": "d3",
            "method": "bar",
            "args": [1, "baz"],
        }
        assert parse_spec(parsing.Math.random) == {
            "pyobsplot-type": "function-object",
            "module": "Math",
            "method": "random",
            "args": (),
        }
        with pytest.raises(ValueError):
            parse_spec(parsing.d3.bar(1, x="baz")) == {
                "pyobsplot-type": "function",
                "module": "d3",
                "method": "bar",
                "args": [1, "baz"],
            }
        assert parse_spec(js("d => d.foo")) == {
            "pyobsplot-type": "js",
            "value": "d => d.foo",
        }


class TestJsModules:
    def test_js_modules(self):
        assert parsing.Plot.foo() == {
            "pyobsplot-type": "function",
            "module": "Plot",
            "method": "foo",
            "args": (),
        }
        assert parsing.d3.bar() == {
            "pyobsplot-type": "function",
            "module": "d3",
            "method": "bar",
            "args": (),
        }
        assert parsing.Math.baz() == {
            "pyobsplot-type": "function",
            "module": "Math",
            "method": "baz",
            "args": (),
        }
        assert parsing.Math.baz() == {
            "pyobsplot-type": "function",
            "module": "Math",
            "method": "baz",
            "args": (),
        }

    def test_js_modules_args(self):
        assert parsing.Plot.foo(1, "bar") == {
            "pyobsplot-type": "function",
            "module": "Plot",
            "method": "foo",
            "args": (1, "bar"),
        }
        assert parsing.Plot.foo([1, 2], {"x": "foo"}) == {
            "pyobsplot-type": "function",
            "module": "Plot",
            "method": "foo",
            "args": ([1, 2], {"x": "foo"}),
        }

    def test_js_modules_kwargs(self):
        with pytest.raises(ValueError, match="kwargs must not be passed to d3\\.foo.*"):
            parsing.d3.foo(x=1)
        with pytest.raises(ValueError, match="kwargs must not be passed to d3\\.bar.*"):
            parsing.d3.bar(12, x=1)

    def test_js(self):
        assert parsing.js("d => d.foo") == {
            "pyobsplot-type": "js",
            "value": "d => d.foo",
        }
