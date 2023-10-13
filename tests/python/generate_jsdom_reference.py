import datetime
import json
import os
import pickle
import sys

import pandas as pd
import polars as pl

from pyobsplot import Obsplot, Plot, js
from pyobsplot.utils import DEFAULT_THEME

# Change working directory to script directory
os.chdir(sys.path[0])

op = Obsplot(renderer="jsdom")
specs = {}
themes = {}
defaults = {}

# Data ---

penguins = pl.read_csv("../../doc/data/penguins.csv")
stocks = pl.read_csv("../../doc/data/stocks.csv", try_parse_dates=True)
simpsons = pl.read_csv("../../doc/data/simpsons.csv")
metros = pl.read_csv("../../doc/data/metros.csv")
stateage = (
    pl.read_csv("../../doc/data/us-population-state-age.csv")
    .melt(id_vars="name", variable_name="age", value_name="population")
    .rename({"name": "state"})
)
with open("../../doc/data/us_states.json") as f:
    us_states = json.load(f)
ca55 = pl.read_csv("../../doc/data/ca55-south.csv")
vapor = (
    pl.read_csv("../../doc/data/vapor.csv", has_header=False, null_values="99999.0")
    .transpose()
    .melt(variable_name="column", value_name="values")
)


# Simple examples ---

specs["simple_svg1.svg"] = Plot.lineY([1, 2, 3, 2])


df = pd.DataFrame(
    {
        "full_date_time": {
            0: pd.Timestamp("2022-12-01 00:00:00"),
            1: pd.Timestamp("2022-12-01 01:00:00"),
        },
        "value": {0: 20.0, 1: 18.0},
    }
)

specs["simple_svg2.svg"] = {
    "marks": [Plot.dot(df, {"x": "full_date_time", "y": "value"})]
}


# Transforms ---

specs["transform_groupx.svg"] = {
    "y": {"grid": True},
    "marks": [
        Plot.barY(penguins, Plot.groupX({"y": "count"}, {"x": "species"})),
        Plot.ruleY([0]),
    ],
}

# Date and times ---

specs["date_dates_js_array.svg"] = {
    "x": {"domain": js("[new Date('2021-01-01'), new Date('2022-01-01')]")},
    "grid": True,
}

specs["date_dates_array_js.svg"] = {
    "x": {"domain": [js("new Date('2021-01-01')"), js("new Date('2022-01-01')")]},
    "grid": True,
}

specs["date_datetime_date.svg"] = {
    "x": {"domain": [datetime.date(2021, 1, 1), datetime.date(2022, 1, 1)]},
    "grid": True,
}

specs["date_datetime_datetime.svg"] = {
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
specs["date_polars_datetime_date.svg"] = {
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
specs["date_polars_datetime_datetime.svg"] = {
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
specs["date_pandas_datetime_date.svg"] = {
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
specs["date_pandas_datetime_datetime.svg"] = {
    "marks": [Plot.dot(d_pd, {"x": "Date", "y": "value"})]
}

# Data sources ---

simpsons_pl = simpsons
simpsons_pd = simpsons_pl.to_pandas()

specs["source_pl_df.svg"] = {
    "marks": [
        Plot.dot(simpsons_pl, {"x": "number_in_season", "y": "imdb_rating"}),
    ]
}

specs["source_pd_df.svg"] = {
    "marks": [
        Plot.dot(simpsons_pd, {"x": "number_in_season", "y": "imdb_rating"}),
    ]
}

specs["source_pl_series.svg"] = {
    "marks": [
        Plot.tickX(simpsons_pl.get_column("imdb_rating"), {"x": "imdb_rating"}),
    ]
}

specs["source_pd_series.svg"] = {
    "marks": [
        Plot.tickX(simpsons_pd["imdb_rating"], {"x": "imdb_rating"}),
    ]
}

# Complex plots ---

specs["complex_simpsons_cells.svg"] = {
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

specs["complex_penguins_facet.svg"] = {
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


specs["complex_metros_arrow.html"] = {
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

specs["complex_stocks.svg"] = {
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

specs["complex_stateage.html"] = {
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

specs["geo_states.html"] = {
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

specs["geo_ca55.svg"] = {
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

specs["geo_vapor.html"] = {
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
            vapor,
            {
                "fill": "values",
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

specs["themes_default.html"] = {
    "color": {"legend": True},
    "marks": [Plot.dot(df, {"x": "x", "fill": "col"})],
}

specs["themes_light.html"] = {
    "color": {"legend": True},
    "marks": [Plot.dot(df, {"x": "x", "fill": "col"})],
}
themes["themes_light.html"] = "light"

specs["themes_dark.html"] = {
    "color": {"legend": True},
    "marks": [Plot.dot(df, {"x": "x", "fill": "col"})],
}
themes["themes_dark.html"] = "dark"

specs["themes_current.html"] = {
    "color": {"legend": True},
    "marks": [Plot.dot(df, {"x": "x", "fill": "col"})],
}
themes["themes_current.html"] = "current"

# Defaults ---

default = {"width": 200, "style": {"color": "white", "background-color": "#005"}}

specs["defaults_svg_no_default.svg"] = Plot.lineY(range(4))
specs["defaults_svg_default.svg"] = Plot.lineY(range(4))
defaults["defaults_svg_default.svg"] = default
specs["defaults_html_no_default.html"] = {
    "color": {"legend": True},
    "marks": [Plot.dot(df, {"x": "x", "fill": "col"})],
}
specs["defaults_html_default.html"] = {
    "color": {"legend": True},
    "marks": [Plot.dot(df, {"x": "x", "fill": "col"})],
}
defaults["defaults_html_default.html"] = default

# utf-8 encoding ---

specs["bug_utf8.html"] = Plot.tickX([-1])
specs["bug_utf8.svg"] = Plot.tickX([-1])


# Main ---

if __name__ == "__main__":
    # Generate output files for each spec
    for key in specs:
        path = f"reference/{key}"
        if not (os.path.exists(path)):
            print(f"Generating {key}")
            if key in themes:
                op.theme = themes[key]
            else:
                op.theme = DEFAULT_THEME
            if key in defaults:
                op.default = defaults[key]
            else:
                op.default = {}
            op(specs[key], path=path)
        else:
            print(f"{key} already exists")
    # Serialize specs, themes and default
    with open("reference/specs.pkl", "wb") as f:
        pickle.dump(specs, f)
    with open("reference/themes.pkl", "wb") as f:
        pickle.dump(themes, f)
    with open("reference/defaults.pkl", "wb") as f:
        pickle.dump(defaults, f)
