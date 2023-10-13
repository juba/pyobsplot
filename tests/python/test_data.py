"""
Tests for data Arrow serialization.
"""

import io

import pandas as pd
import polars as pl
import pyarrow as pa

from pyobsplot.data import arrow_schema_no_big, pd_to_arrow, pl_to_arrow


class TestSchemaNoBig:
    def test_arrow_schema_no_big(self):
        df = pl.DataFrame(
            {
                "i": [1, 2],
                "f": [1.0, 2.0],
                "s": ["foo", "bar"],
                "i2": [3, 4],
                "cat1": ["foo", "bar"],
                "cat2": ["foo", "bar"],
            },
            schema={
                "i": pl.Int64,
                "f": pl.Float64,
                "s": pl.Utf8,
                "i2": pl.Int32,
                "cat1": pl.Categorical,
                "cat2": pl.Categorical,
            },
        )
        df = df.with_columns(pl.col("cat2").cat.set_ordering("lexical"))
        schema = df.to_arrow().schema
        assert schema.names == ["i", "f", "s", "i2", "cat1", "cat2"]
        assert schema.types == [
            pa.int64(),
            pa.float64(),
            pa.large_string(),
            pa.int32(),
            pa.dictionary(pa.uint32(), pa.large_string(), ordered=False),
            pa.dictionary(pa.uint32(), pa.large_string(), ordered=False),
        ]
        schema_no_big = arrow_schema_no_big(schema)
        assert schema_no_big.names == ["i", "f", "s", "i2", "cat1", "cat2"]
        assert schema_no_big.types == [
            pa.int32(),
            pa.float32(),
            pa.string(),
            pa.int32(),
            pa.dictionary(pa.uint32(), pa.string(), ordered=False),
            pa.dictionary(pa.uint32(), pa.string(), ordered=False),
        ]


class TestDataFrame:
    def test_data_frame_pandas(self):
        df = pd.DataFrame({"i": [1, 2], "f": [1.0, 2.0], "s": ["foo", "bar"]})
        df_arrow = pd_to_arrow(df)
        f = io.BytesIO(df_arrow)
        df_arrow = pa.feather.read_feather(f)
        assert df_arrow.equals(df)

    def test_data_frame_polars(self):
        df = pl.DataFrame(
            {
                "i": [1, 2],
                "f": [1.0, 2.0],
                "s": ["foo", "bar"],
            },
            schema={
                "i": pl.Int64,
                "f": pl.Float64,
                "s": pl.Utf8,
            },
        )
        df_arrow = pl_to_arrow(df)
        f = io.BytesIO(df_arrow)
        df_arrow = pl.read_ipc(f)
        assert df_arrow.frame_equal(df)
        assert df_arrow.dtypes == [
            pl.Int32,
            pl.Float32,
            pl.Utf8,
        ]
