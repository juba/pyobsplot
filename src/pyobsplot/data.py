"""
Functions for DataFrame objects conversion to Arrow IPC bytes.
"""

import base64
import io
from typing import Any

import pandas as pd
import polars as pl


def serialize(data: Any, renderer: str) -> Any:
    """
    Serialize a data object.

    Parameters
    ----------
    data : Any
        data object to serialize.
    renderer : str
        renderer type.

    Returns
    -------
    Any
        serialized data object.
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
    """
    Convert a pandas DataFrame to Arrow IPC bytes.

    Parameters
    ----------
    df : pd.DataFrame
        pandas DataFrame to convert.

    Returns
    -------
    bytes
        Arrow IPC bytes.
    """
    # Convert dates to timestamps
    for col in df.columns:
        if df[col].dtype == "object":
            try:
                df[col] = pd.to_datetime(df[col])
            except ValueError:
                pass
    # Convert timestamps to millisecond units so that
    # Plot will detect them as datetimes
    datetime_columns = df.select_dtypes(include=["datetime64"]).columns
    df[datetime_columns] = df[datetime_columns].astype("datetime64[ms]")

    f = io.BytesIO()
    df.to_feather(f, compression="uncompressed")
    return f.getvalue()


def pl_to_arrow(df: pl.DataFrame) -> bytes:
    """
    Convert a polars DataFrame to Arrow IPC bytes.

    Parameters
    ----------
    df : pl.DataFrame
        polars DataFrame to convert.

    Returns
    -------
    bytes
        Arrow IPC bytes.
    """

    # Convert dates and datetimes to millisecond units so that
    # Plot will detect them as datetimes
    df = df.with_columns(pl.col(pl.Datetime).cast(pl.Datetime("ms")))
    df = df.with_columns(pl.col(pl.Date).cast(pl.Datetime("ms")))

    f = io.BytesIO()
    df_pd = df.to_pandas()
    df_pd.to_feather(f, compression="uncompressed")
    return f.getvalue()
