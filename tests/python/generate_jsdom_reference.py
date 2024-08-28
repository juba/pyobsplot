import datetime
import json
import logging
import os
import pickle
import sys
from pathlib import Path

import pandas as pd
import polars as pl

from pyobsplot import Obsplot, Plot, js
from pyobsplot.utils import DEFAULT_THEME

logger = logging.getLogger("generate-jsdom")
logging.basicConfig(stream=sys.stdout, level=logging.INFO, format="%(message)s")

# Change working directory to script directory
os.chdir(sys.path[0])

specs = {}
themes = {}
defaults = {}
skip = {}

# Data ---

penguins = pl.read_csv("../../doc/data/penguins.csv")
stocks = pl.read_csv("../../doc/data/stocks.csv", try_parse_dates=True)
simpsons = pl.read_csv("../../doc/data/simpsons.csv").filter(
    pl.col("imdb_rating").is_not_null()
)
metros = pl.read_csv("../../doc/data/metros.csv")
stateage = (
    pl.read_csv("../../doc/data/us-population-state-age.csv")
    .unpivot(index="name", variable_name="age", value_name="population")
    .rename({"name": "state"})
)
# TODO: remove when Bigint error fixed upstream in Observable Plot
stateage = stateage.with_columns(pl.col("population").cast(pl.Int32))
with open("../../doc/data/us_states.json") as f:
    us_states = json.load(f)
ca55 = pl.read_csv("../../doc/data/ca55-south.csv")
vapor = (
    pl.read_csv("../../doc/data/vapor.csv", has_header=False, null_values="99999.0")
    .transpose()
    .unpivot(variable_name="column", value_name="values")
)
vapor_values = vapor.get_column("values").to_list()


# Simple examples ---

specs["simple_svg1"] = Plot.lineY([1, 2, 3, 2])


df = pd.DataFrame(
    {
        "full_date_time": {
            0: pd.Timestamp("2022-12-01 00:00:00"),
            1: pd.Timestamp("2022-12-01 01:00:00"),
        },
        "value": {0: 20.0, 1: 18.0},
    }
)

specs["simple_svg2"] = {"marks": [Plot.dot(df, {"x": "full_date_time", "y": "value"})]}


# Titles and caption ---

specs["titles_caption"] = {
    "marks": [Plot.dot(df, {"x": "full_date_time", "y": "value"})],
    "title": "This is a plot title",
    "subtitle": "This is a plot subtitle",
    "caption": (
        "And here is a plot caption long enough to span"
        " over several lines in the generated output."
    ),
}


# Transforms ---

specs["transform_groupx"] = {
    "y": {"grid": True},
    "marks": [
        Plot.barY(penguins, Plot.groupX({"y": "count"}, {"x": "species"})),
        Plot.ruleY([0]),
    ],
}

# Date and times ---

specs["date_dates_js_array"] = {
    "x": {"domain": js("[new Date('2021-01-01'), new Date('2022-01-01')]")},
    "grid": True,
}

specs["date_dates_array_js"] = {
    "x": {"domain": [js("new Date('2021-01-01')"), js("new Date('2022-01-01')")]},
    "grid": True,
}

specs["date_datetime_date"] = {
    "x": {"domain": [datetime.date(2021, 1, 1), datetime.date(2022, 1, 1)]},
    "grid": True,
}

specs["date_datetime_datetime"] = {
    "x": {
        "type": "time",
        "domain": [
            datetime.datetime(2021, 1, 1, 8, 0, 0),
            datetime.datetime(2021, 1, 1, 8, 1, 0),
        ],
    },
    "grid": True,
}


d_pl = pl.DataFrame(
    {
        "Date": [
            datetime.date(2021, 1, 1),
            datetime.date(2021, 1, 2),
            datetime.date(2021, 1, 3),
        ],
        "value": [1, 2, 3],
    }
)
specs["date_polars_datetime_date"] = {
    "marks": [Plot.dot(d_pl, {"x": "Date", "y": "value"})]
}

d_pl = pl.DataFrame(
    {
        "Date": [
            datetime.datetime(2021, 1, 1, 8, 0, 0),
            datetime.datetime(2021, 1, 1, 8, 0, 1),
            datetime.datetime(2021, 1, 1, 8, 0, 2),
        ],
        "value": [1, 2, 3],
    }
)
specs["date_polars_datetime_datetime"] = {
    "marks": [Plot.dot(d_pl, {"x": "Date", "y": "value"})]
}

d_pd = pd.DataFrame(
    {
        "Date": [
            datetime.date(2021, 1, 1),
            datetime.date(2021, 1, 2),
            datetime.date(2021, 1, 3),
        ],
        "value": [1, 2, 3],
    }
)
specs["date_pandas_datetime_date"] = {
    "marks": [Plot.dot(d_pd, {"x": "Date", "y": "value"})]
}

d_pd = pd.DataFrame(
    {
        "Date": [
            datetime.datetime(2021, 1, 1, 8, 0, 0),
            datetime.datetime(2021, 1, 1, 8, 0, 1),
            datetime.datetime(2021, 1, 1, 8, 0, 2),
        ],
        "value": [1, 2, 3],
    }
)
specs["date_pandas_datetime_datetime"] = {
    "marks": [Plot.dot(d_pd, {"x": "Date", "y": "value"})]
}

# Data sources ---

simpsons_pl = simpsons
simpsons_pd = simpsons_pl.to_pandas()

specs["source_pl_df"] = {
    "marks": [
        Plot.dot(simpsons_pl, {"x": "number_in_season", "y": "imdb_rating"}),
    ]
}

specs["source_pd_df"] = {
    "marks": [
        Plot.dot(simpsons_pd, {"x": "number_in_season", "y": "imdb_rating"}),
    ]
}

specs["source_pl_series"] = {
    "marks": [
        Plot.tickX(simpsons_pl.get_column("imdb_rating"), {"x": "imdb_rating"}),
    ]
}

specs["source_pd_series"] = {
    "marks": [
        Plot.tickX(simpsons_pd["imdb_rating"], {"x": "imdb_rating"}),
    ]
}

# Complex plots ---

specs["complex_simpsons_cells"] = {
    "height": 640,
    "padding": 0.05,
    "grid": True,
    "x": {"axis": "top", "label": "Season"},
    "y": {"label": "Episode"},
    "color": {"type": "linear", "scheme": "PiYG"},
    "marks": [
        Plot.cell(
            simpsons, {"x": "season", "y": "number_in_season", "fill": "imdb_rating"}
        ),
        Plot.text(
            simpsons,
            {
                "x": "season",
                "y": "number_in_season",
                "text": "imdb_rating",
                "title": "title",
            },
        ),
    ],
}

specs["complex_penguins_facet"] = {
    "height": 600,
    "grid": True,
    "facet": {"data": penguins, "x": "sex", "y": "species", "marginRight": 80},
    "marks": [
        Plot.frame({"facet": False}),
        Plot.dot(
            penguins,
            {
                "x": "culmen_depth_mm",
                "y": "culmen_length_mm",
                "r": 1.5,
                "fill": "#ccc",
                "facet": "exclude",
            },
        ),
        Plot.dot(
            penguins,
            {"x": "culmen_depth_mm", "y": "culmen_length_mm", "facet": True},
        ),
    ],
}


specs["complex_metros_arrow"] = {
    "height": 600,
    "grid": True,
    "inset": 10,
    "x": {"type": "log", "label": "Population →"},
    "y": {"label": "↑ Inequality", "ticks": 4},
    "color": {
        "type": "diverging",
        "scheme": "burd",
        "label": "Change in inequality from 1980 to 2015",
        "legend": True,
        "ticks": 6,
        "tickFormat": "+f",
    },
    "marks": [
        Plot.arrow(
            metros,
            {
                "x1": "POP_1980",
                "y1": "R90_10_1980",
                "x2": "POP_2015",
                "y2": "R90_10_2015",
                "bend": True,
                "stroke": js("d => d.R90_10_2015 - d.R90_10_1980"),
            },
        ),
        Plot.text(
            metros,
            {
                "x": "POP_2015",
                "y": "R90_10_2015",
                "filter": "highlight",
                "text": "nyt_display",
                "fill": "currentColor",
                "stroke": "white",
                "dy": -6,
            },
        ),
    ],
}

specs["complex_stocks"] = {
    "marginRight": 40,
    "y": {
        "type": "log",
        "grid": True,
        "label": "↑ Change in price (%)",
        "tickFormat": js('(f => x => f((x - 1) * 100))(d3.format("+d"))'),
    },
    "marks": [
        Plot.ruleY([1]),
        Plot.line(
            stocks, Plot.normalizeY({"x": "Date", "y": "Close", "stroke": "Symbol"})
        ),
        Plot.text(
            stocks,
            Plot.selectLast(
                Plot.normalizeY(
                    {
                        "x": "Date",
                        "y": "Close",
                        "z": "Symbol",
                        "text": "Symbol",
                        "textAnchor": "start",
                        "dx": 3,
                    }
                )
            ),
        ),
    ],
}


ages = stateage.get_column("age").unique(maintain_order=True).to_list()
states = (
    stateage.with_columns(
        (pl.col("population") / pl.col("population").sum().over("state")).alias(
            "percent"
        )
    )
    .filter(pl.col("age") == "≥80")
    .sort(pl.col("percent"), descending=True)
    .get_column("state")
    .to_list()
)

xy = {"basis": "sum", "z": "state", "x": "population", "y": "state"}

specs["complex_stateage"] = {
    "height": 660,
    "grid": True,
    "x": {"axis": "top", "label": "Percent (%) →", "transform": js("d => d * 100")},
    "y": {
        "domain": states,
        "axis": None,
    },
    "color": {"scheme": "spectral", "domain": ages, "legend": True},
    "marks": [
        Plot.ruleX([0]),
        Plot.ruleY(
            stateage,
            Plot.groupY({"x1": "min", "x2": "max"}, Plot.normalizeX(xy)),
        ),
        Plot.dot(
            stateage,
            Plot.normalizeX({**xy, "fill": "age"}),
        ),
        Plot.text(
            stateage,
            Plot.selectMinX(
                Plot.normalizeX(
                    {
                        **xy,
                        "textAnchor": "end",
                        "dx": -6,
                        "text": "state",
                    }
                )
            ),
        ),
    ],
}

# Geo ---

specs["geo_states"] = {
    "projection": "albers-usa",
    "color": {
        "type": "quantile",
        "n": 8,
        "scheme": "blues",
        "label": "Unemployment (%)",
        "legend": True,
    },
    "marks": [Plot.geo(us_states, {"fill": "grey", "stroke": "white"})],
}

projection = {
    "type": "mercator",
    "domain": {
        "type": "MultiPoint",
        "coordinates": ca55.select(["LONGITUDE", "LATITUDE"]),
    },
}

specs["geo_ca55"] = {
    "data": "projection",
    "x": {"axis": None},
    "y": {"axis": None},
    "inset": 10,
    "margin": 10,
    "height": 500,
    "marginBottom": 2,
    "color": {"type": "diverging"},
    "marks": [
        Plot.raster(
            ca55,
            {
                "x": "LONGITUDE",
                "y": "LATITUDE",
                "fill": "MAG_IGRF90",
                "interpolate": "random-walk",
            },
        ),
        Plot.frame(),
    ],
}

specs["geo_vapor"] = {
    "projection": "equal-earth",
    "color": {
        "scheme": "blues",
        "legend": True,
        "ticks": 6,
        "nice": True,
        "label": "Water vapor (cm)",
    },
    "marks": [
        Plot.contour(
            vapor_values,
            {
                "fill": Plot.identity,
                "width": 360,
                "height": 180,
                "x1": -180,
                "y1": 90,
                "x2": 180,
                "y2": -90,
                "interval": 0.25,
                "blur": 0.5,
                "interpolate": "barycentric",
                "stroke": "currentColor",
                "strokeWidth": 0.5,
                "clip": "sphere",
            },
        ),
        Plot.sphere(),
    ],
}

# Themes ---

df = pl.DataFrame({"x": range(4), "col": list("AABB")})

specs["themes_default"] = {
    "color": {"legend": True},
    "marks": [Plot.dot(df, {"x": "x", "fill": "col"})],
}

specs["themes_light"] = {
    "color": {"legend": True},
    "marks": [Plot.dot(df, {"x": "x", "fill": "col"})],
}
themes["themes_light"] = "light"

specs["themes_dark"] = {
    "color": {"legend": True},
    "marks": [Plot.dot(df, {"x": "x", "fill": "col"})],
}
themes["themes_dark"] = "dark"

specs["themes_current"] = {
    "color": {"legend": True},
    "marks": [Plot.dot(df, {"x": "x", "fill": "col"})],
}
themes["themes_current"] = "current"
skip["themes_current"] = ["png", "pdf", "svg"]

# Defaults ---

default = {"width": 200, "style": {"color": "white", "background-color": "#005"}}

specs["defaults_svg_no_default"] = Plot.lineY(range(4))
specs["defaults_svg_default"] = Plot.lineY(range(4))
defaults["defaults_svg_default"] = default
specs["defaults_html_no_default"] = {
    "color": {"legend": True},
    "marks": [Plot.dot(df, {"x": "x", "fill": "col"})],
}
specs["defaults_html_default"] = {
    "color": {"legend": True},
    "marks": [Plot.dot(df, {"x": "x", "fill": "col"})],
}
defaults["defaults_html_default"] = default

# utf-8 encoding ---

specs["bug_utf8"] = Plot.tickX([-1])
specs["bug_utf8"] = Plot.tickX([-1])


# Main ---


def generate_format(format: str, output_folder: Path) -> None:  # noqa: A002
    output_folder = output_folder / format
    output_folder.mkdir(exist_ok=True)
    for key in specs:
        if key in skip and format in skip[key]:
            continue
        path = output_folder / f"{key}.{format}"
        if not (path.exists()):
            logger.info(f"Generating {key}.{format}")
            if key in themes:
                op.theme = themes[key]
            else:
                op.theme = DEFAULT_THEME
            if key in defaults:
                op.default = defaults[key]
            else:
                op.default = {}
            format_value = None if format == "pdf" else format
            op(specs[key], format=format_value, path=path)  # type: ignore
        else:
            logger.info(f"{key}.{format} already exists")


if __name__ == "__main__":
    # Generate output files for each spec
    op = Obsplot()
    output_folder = Path("./jsdom_reference")
    for format in ("html", "png", "pdf", "svg"):  # noqa: A001
        generate_format(format, output_folder)
    # Serialize specs, themes and default
    with open(output_folder / "specs.pkl", "wb") as f:
        pickle.dump(specs, f)
    with open(output_folder / "themes.pkl", "wb") as f:
        pickle.dump(themes, f)
    with open(output_folder / "defaults.pkl", "wb") as f:
        pickle.dump(defaults, f)
