"""
Tests for specification parsing.
"""

import pytest

import pandas as pd
import polars as pl
import datetime

from pyobsplot import js_modules, Plot
from pyobsplot.parsing import SpecParser, js
from pyobsplot.data import pd_to_arrow, pl_to_arrow


class TestSpecParser:
    def test_specparser_init(self):
        parser = SpecParser()
        assert parser.renderer == "widget"
        assert parser._spec == {}
        assert parser._default == {}
        parser = SpecParser(renderer="widget", default={"foo": "bar"})
        assert parser.renderer == "widget"
        assert parser._spec == {}
        assert parser._default == {"foo": "bar"}
        parser = SpecParser(renderer="jsdom")
        assert parser.renderer == "jsdom"
        assert parser._spec == {}
        assert parser._default == {}
        parser = SpecParser(renderer="jsdom", default={"foo": "bar"})
        assert parser.renderer == "jsdom"
        assert parser._spec == {}
        assert parser._default == {"foo": "bar"}

    def test_parse_plot_mark(self):
        parser = SpecParser()
        parser.spec = Plot.lineY([1, 2, 3])  # type: ignore
        assert parser.spec == {
            "marks": [
                {
                    "pyobsplot-type": "function",
                    "module": "Plot",
                    "method": "lineY",
                    "args": ([1, 2, 3],),
                }
            ]
        }


class TestMergedefault:
    def test_merge_without_default(self):
        spec = {"width": 100, "color": {"legend": True}}
        parser = SpecParser(renderer="widget")
        parser.spec = spec
        parsed = parser.parse_spec()
        assert parsed == spec
        parser = SpecParser(renderer="jsdom")
        parser.spec = spec
        parsed = parser.parse_spec()
        assert parsed == spec

    def test_merge_with_default(self):
        spec = {"width": 100, "color": {"legend": True}}
        default = {"width": 200, "style": {"color": "red"}}
        merged = {"width": 100, "color": {"legend": True}, "style": {"color": "red"}}
        parser = SpecParser(renderer="widget", default=default)
        parser.spec = spec
        parsed = parser.parse_spec()
        assert parsed == merged
        parser = SpecParser(renderer="jsdom", default=default)
        parser.spec = spec
        parsed = parser.parse_spec()
        assert parsed == merged


class TestParse:
    def test_parse_none(self):
        assert SpecParser().parse(None) is None

    def test_parse_recursive(self):
        assert SpecParser().parse([1, "foo", None]) == [1, "foo", None]
        assert SpecParser().parse((1, "foo", None)) == [1, "foo", None]
        assert SpecParser().parse({"x": 1, "y": "foo", "z": None}) == {
            "x": 1,
            "y": "foo",
            "z": None,
        }

    def test_parse_range(self):
        parser = SpecParser()
        parsed = parser.parse(range(3))
        assert parsed == [0, 1, 2]

    def test_parse_geojson(self):
        df = pd.DataFrame({"x": [1, 2], "y": [1, 3]})
        parser = SpecParser()
        # Geojson as dict
        parsed = parser.parse({"type": "FeatureCollection", "val": df})
        assert parsed == {"pyobsplot-type": "GeoJson-ref", "value": 0}
        assert parser.data == [
            {
                "type": "FeatureCollection",
                "val": df,
            }
        ]
        # Geojson as string
        parsed = parser.parse('{"type": "FeatureCollection", "val": [1, 2]}')
        assert parsed == {"pyobsplot-type": "GeoJson-ref", "value": 1}
        assert parser.data[1] == {
            "type": "FeatureCollection",
            "val": [1, 2],
        }

    def test_parse_dataframe(self):
        df_pd = pd.DataFrame({"x": [1, 2], "y": ["foo", "bar"]})
        df_pl = pl.DataFrame({"x": [1, 2], "y": ["foo", "bar"]})
        parser_pd = SpecParser()
        parsed_pd = parser_pd.parse(df_pd)
        assert parsed_pd == {
            "pyobsplot-type": "DataFrame-ref",
            "value": 0,
        }
        assert parser_pd.data == [df_pd]
        assert parser_pd.serialize_data()[0] == {
            "pyobsplot-type": "DataFrame",
            "value": pd_to_arrow(df_pd),
        }
        parser_pl = SpecParser()
        parsed_pl = parser_pl.parse(df_pl)
        assert parsed_pl == {
            "pyobsplot-type": "DataFrame-ref",
            "value": 0,
        }
        assert parser_pl.data == [df_pl]
        assert parser_pl.serialize_data()[0] == {
            "pyobsplot-type": "DataFrame",
            "value": pl_to_arrow(df_pl),
        }

    def test_parse_series(self):
        df_pd = pd.DataFrame({"x": [1, 2], "y": ["foo", "bar"]})
        series_pd = df_pd["x"]
        df_pl = pl.DataFrame({"x": [1, 2], "y": ["foo", "bar"]})
        series_pl = df_pl.get_column("x")
        parser_pd = SpecParser()
        parsed_pd = parser_pd.parse(series_pd)
        assert parsed_pd == {
            "pyobsplot-type": "DataFrame-ref",
            "value": 0,
        }
        assert parser_pd.data[0].equals(pd.DataFrame(df_pd["x"]))
        assert parser_pd.serialize_data()[0] == {
            "pyobsplot-type": "DataFrame",
            "value": pd_to_arrow(pd.DataFrame(df_pd["x"])),
        }
        parser_pl = SpecParser()
        parsed_pl = parser_pl.parse(series_pl)
        assert parsed_pl == {
            "pyobsplot-type": "DataFrame-ref",
            "value": 0,
        }
        assert parser_pl.data[0].frame_equal(pl.DataFrame(df_pl.get_column("x")))
        assert parser_pl.serialize_data()[0] == {
            "pyobsplot-type": "DataFrame",
            "value": pl_to_arrow(pl.DataFrame(df_pl.get_column("x"))),
        }

    def test_parse_datetime(self):
        assert SpecParser().parse(datetime.date(2023, 1, 1)) == {
            "pyobsplot-type": "datetime",
            "value": "2023-01-01",
        }
        assert SpecParser().parse(datetime.datetime(2023, 1, 1, 14, 25, 12)) == {
            "pyobsplot-type": "datetime",
            "value": "2023-01-01T14:25:12",
        }

    def test_parse_js(self):
        assert SpecParser().parse(js_modules.Plot.dot()) == {  # type: ignore
            "pyobsplot-type": "function",
            "module": "Plot",
            "method": "dot",
            "args": [],
        }
        assert SpecParser().parse(js_modules.d3.bar(1, "baz")) == {
            "pyobsplot-type": "function",
            "module": "d3",
            "method": "bar",
            "args": [1, "baz"],
        }
        assert SpecParser().parse(js_modules.Math.random) == {
            "pyobsplot-type": "function-object",
            "module": "Math",
            "method": "random",
            "args": (),
        }
        with pytest.raises(ValueError):
            SpecParser().parse(js_modules.d3.bar(1, x="baz")) == {
                "pyobsplot-type": "function",
                "module": "d3",
                "method": "bar",
                "args": [1, "baz"],
            }  # type: ignore
        assert SpecParser().parse(js("d => d.foo")) == {
            "pyobsplot-type": "js",
            "value": "d => d.foo",
        }

    def test_parse_caching_polars(self):
        df_pl = pl.DataFrame({"x": [1, 2], "y": ["foo", "bar"]})
        df_pl2 = pl.DataFrame({"x": [3, 4], "y": ["foo", "bar"]})
        df_pl_copy = df_pl
        spec = {"x": df_pl, "y": df_pl2, "z": df_pl, "u": df_pl_copy, "w": df_pl2}
        parser = SpecParser()
        parsed = parser.parse(spec)
        assert len(parser.data) == 2
        assert parser.data[0].frame_equal(df_pl)
        assert parser.data[1].frame_equal(df_pl2)
        assert parsed["x"] == {"pyobsplot-type": "DataFrame-ref", "value": 0}
        assert parsed["y"] == {"pyobsplot-type": "DataFrame-ref", "value": 1}
        assert parsed["z"] == {"pyobsplot-type": "DataFrame-ref", "value": 0}
        assert parsed["u"] == {"pyobsplot-type": "DataFrame-ref", "value": 0}
        assert parsed["w"] == {"pyobsplot-type": "DataFrame-ref", "value": 1}
        assert parser.serialize_data()[0] == {
            "pyobsplot-type": "DataFrame",
            "value": pl_to_arrow(df_pl),
        }
        assert parser.serialize_data()[1] == {
            "pyobsplot-type": "DataFrame",
            "value": pl_to_arrow(df_pl2),
        }

    def test_parse_caching_pandas(self):
        df_pd = pd.DataFrame({"x": [1, 2], "y": ["foo", "bar"]})
        df_pd2 = pd.DataFrame({"x": [3, 4], "y": ["foo", "bar"]})
        df_pd_copy = df_pd
        spec = {"x": df_pd, "y": df_pd2, "z": df_pd, "u": df_pd_copy, "w": df_pd2}
        parser = SpecParser()
        parsed = parser.parse(spec)
        assert len(parser.data) == 2
        assert parser.data[0].equals(df_pd)
        assert parser.data[1].equals(df_pd2)
        assert parsed["x"] == {"pyobsplot-type": "DataFrame-ref", "value": 0}
        assert parsed["y"] == {"pyobsplot-type": "DataFrame-ref", "value": 1}
        assert parsed["z"] == {"pyobsplot-type": "DataFrame-ref", "value": 0}
        assert parsed["u"] == {"pyobsplot-type": "DataFrame-ref", "value": 0}
        assert parsed["w"] == {"pyobsplot-type": "DataFrame-ref", "value": 1}
        assert parser.serialize_data()[0] == {
            "pyobsplot-type": "DataFrame",
            "value": pd_to_arrow(df_pd),
        }
        assert parser.serialize_data()[1] == {
            "pyobsplot-type": "DataFrame",
            "value": pd_to_arrow(df_pd2),
        }

    def test_parse_caching_geojson(self):
        geo = {"type": "FeatureCollection", "x": 1, "y": "foo"}
        geo2 = {"type": "FeatureCollection", "x": 1, "y": "foo"}
        geo_copy = geo
        spec = {"x": geo, "y": geo2, "z": geo, "u": geo_copy, "w": geo2}
        parser = SpecParser()
        parsed = parser.parse(spec)
        assert len(parser.data) == 2
        assert parser.data[0] is geo
        assert parser.data[1] is geo2
        assert parsed["x"] == {"pyobsplot-type": "GeoJson-ref", "value": 0}
        assert parsed["y"] == {"pyobsplot-type": "GeoJson-ref", "value": 1}
        assert parsed["z"] == {"pyobsplot-type": "GeoJson-ref", "value": 0}
        assert parsed["u"] == {"pyobsplot-type": "GeoJson-ref", "value": 0}
        assert parsed["w"] == {"pyobsplot-type": "GeoJson-ref", "value": 1}
        assert parser.serialize_data()[0] == geo
        assert parser.serialize_data()[1] == geo2

    def test_parse_caching_mixed(self):
        geo = {"type": "FeatureCollection", "x": 1, "y": "foo"}
        df_pl = pl.DataFrame({"x": [1, 2], "y": ["foo", "bar"]})
        df_pd = pd.DataFrame({"x": [1, 2], "y": ["foo", "bar"]})
        spec = {"x": geo, "y": df_pl, "z": df_pd, "u": geo, "v": df_pl, "w": df_pd}
        parser = SpecParser()
        parsed = parser.parse(spec)
        assert len(parser.data) == 3
        assert parser.data[0] is geo
        assert parser.data[1] is df_pl
        assert parser.data[2] is df_pd
        assert parsed["x"] == {"pyobsplot-type": "GeoJson-ref", "value": 0}
        assert parsed["y"] == {"pyobsplot-type": "DataFrame-ref", "value": 1}
        assert parsed["z"] == {"pyobsplot-type": "DataFrame-ref", "value": 2}
        assert parsed["u"] == {"pyobsplot-type": "GeoJson-ref", "value": 0}
        assert parsed["v"] == {"pyobsplot-type": "DataFrame-ref", "value": 1}
        assert parsed["w"] == {"pyobsplot-type": "DataFrame-ref", "value": 2}
        assert parser.serialize_data()[0] == geo
        assert parser.serialize_data()[1] == {
            "pyobsplot-type": "DataFrame",
            "value": pl_to_arrow(df_pl),
        }
        assert parser.serialize_data()[2] == {
            "pyobsplot-type": "DataFrame",
            "value": pd_to_arrow(df_pd),
        }
