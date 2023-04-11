"""
Functions for DataFrame objects conversion to Arrow IPC bytes.
"""


import io
import pandas as pd
import polars as pl
import pyarrow as pa
import pyarrow.feather as pf
import base64

from typing import Any


def serialize(data: Any, renderer: str) -> Any:
    """Serialize a data object.

    Args:
        data (Any): data object to serialize.
        renderer (str): renderer.

    Returns:
        Any: serialized data object.
    """
    # If polars DataFrame, serialize to Arrow IPC
    if isinstance(data, pl.DataFrame):
        value = pl_to_arrow(data)
        if renderer == "jsdom":
            value = base64.standard_b64encode(value).decode("ascii")
        return {"pyobsplot-type": "DataFrame", "value": value}
    # If pandas DataFrame, serialize to Arrow IPC
    elif isinstance(data, pd.DataFrame):
        value = pd_to_arrow(data)
        if renderer == "jsdom":
            value = base64.standard_b64encode(value).decode("ascii")
        return {"pyobsplot-type": "DataFrame", "value": value}
    # Else, keep as is
    else:
        return data


def pd_to_arrow(df: pd.DataFrame) -> bytes:
    """Convert a pandas DataFrame to Arrow IPC bytes.

    Args:
        df (pd.DataFrame): pandas DataFrame to convert.

    Returns:
        bytes: Arrow IPC bytes
    """
    f = io.BytesIO()
    df.to_feather(f, compression="uncompressed")
    return f.getvalue()


def pl_to_arrow(df: pl.DataFrame) -> bytes:
    """Convert a polars DataFrame to Arrow IPC bytes.

    Args:
        df (pl.DataFrame): polars DataFrame to convert.

    Returns:
        bytes: Arrow IPC bytes.
    """

    pa_table = df.to_arrow()
    pa_table_no_big = pa_table.cast(arrow_schema_no_big(pa_table.schema))

    f = io.BytesIO()
    pf.write_feather(pa_table_no_big, f, compression="uncompressed")
    return f.getvalue()


def arrow_schema_no_big(pa_schema: Any) -> Any:
    """Transform a pyarrow schema by converting large strings to strings,
    float64 to float32 and int64 to int32. This is needed because JavaScript
    apache-arrow library doesn't support large types yet.

    Args:
        pa_schema (Any): schema to convert.

    Returns:
        Any: conversion result.
    """
    pa_schema_no_big = []
    for col_name, pa_dtype in zip(pa_schema.names, pa_schema.types):
        # Large strings to string
        if pa_dtype == pa.large_string():
            pa_schema_no_big.append(pa.field(col_name, pa.string()))
        # Int64 to Int32
        elif pa_dtype == pa.int64():
            pa_schema_no_big.append(pa.field(col_name, pa.int32()))
        # Float64 to Float32
        elif pa_dtype == pa.float64():
            pa_schema_no_big.append(pa.field(col_name, pa.float32()))
        # Large strings in dictionaries to string (for polars Categorical)
        elif pa_dtype == pa.dictionary(pa.uint32(), pa.large_string(), ordered=False):
            pa_schema_no_big.append(
                pa.field(
                    col_name, pa.dictionary(pa.uint32(), pa.string(), ordered=False)
                )
            )
        elif pa_dtype == pa.dictionary(pa.uint32(), pa.large_string(), ordered=True):
            pa_schema_no_big.append(
                pa.field(
                    col_name, pa.dictionary(pa.uint32(), pa.string(), ordered=True)
                )
            )
        else:
            pa_schema_no_big.append(pa.field(col_name, pa_dtype))
    return pa.schema(pa_schema_no_big)
