"""
Functions for DataFrame objects conversion to Arrow IPC bytes.
"""

import base64
import io
from typing import Any

import pandas as pd
import polars as pl
import pyarrow as pa
import pyarrow.feather as pf


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

    f = io.BytesIO()
    pf.write_feather(df.to_arrow(), f, compression="uncompressed")
    return f.getvalue()
