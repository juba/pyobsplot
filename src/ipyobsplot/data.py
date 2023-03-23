import io
import pandas as pd
import polars as pl
import pyarrow as pa
import pyarrow.feather as pf


def pd_to_arrow(df: pd.DataFrame) -> str:
    f = io.BytesIO()
    df.to_feather(f, compression="uncompressed")
    return f.getvalue()


def pl_to_arrow(df: pl.DataFrame) -> str:
    def arrow_schema_no_big(pa_schema):
        pa_schema_no_big = []
        for col_name, pa_dtype in zip(pa_schema.names, pa_schema.types):
            if pa_dtype == pa.large_string():
                pa_schema_no_big.append(pa.field(col_name, pa.string()))
            elif pa_dtype == pa.int64():
                pa_schema_no_big.append(pa.field(col_name, pa.int32()))
            elif pa_dtype == pa.float64():
                pa_schema_no_big.append(pa.field(col_name, pa.float32()))
            else:
                pa_schema_no_big.append(pa.field(col_name, pa_dtype))
        return pa.schema(pa_schema_no_big)

    pa_table = df.to_arrow()
    pa_table_no_big = pa_table.cast(arrow_schema_no_big(pa_table.schema))

    f = io.BytesIO()
    pf.write_feather(pa_table_no_big, f, compression="uncompressed")
    return f.getvalue()
