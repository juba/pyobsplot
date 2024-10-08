"""
Tests for data Arrow serialization.
"""

import io

import pandas as pd
import polars as pl
from polars.testing import assert_frame_equal
from pyarrow import feather

from pyobsplot.data import pd_to_arrow, pl_to_arrow


class TestDataFrame:
    def test_data_frame_pandas(self):
        df = pd.DataFrame({"i": [1, 2], "f": [1.0, 2.0], "s": ["foo", "bar"]})
        df_arrow = pd_to_arrow(df)
        f = io.BytesIO(df_arrow)
        df_arrow = feather.read_feather(f)
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
        assert_frame_equal(df_arrow, df)
        assert df_arrow.dtypes == [
            pl.Int64,
            pl.Float64,
            pl.Utf8,
        ]
