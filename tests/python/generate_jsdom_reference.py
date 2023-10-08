from pyobsplot import Obsplot, Plot, d3, js
import pandas as pd
import polars as pl
import pickle
import os
import sys

# Change working directory to script directory
os.chdir(sys.path[0])

op = Obsplot(renderer="jsdom")
specs = dict()


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

stocks = pl.read_csv("../../doc/data/stocks.csv", try_parse_dates=True)

specs["stocks.html"] = {
    "y": {"grid": True},
    "color": {"legend": True},
    "marks": [
        Plot.lineY(stocks, {"x": "Date", "y": "Close", "stroke": "Symbol", "tip": True})
    ],
}

penguins = pl.read_csv("../doc/data/penguins.csv")

specs["penguins.html"] == {
    "inset": 20,
    "grid": True,
    "facet": {"data": penguins, "x": "sex"},
    "marks": [
        Plot.dot(penguins, {"x": "culmen_depth_mm", "y": "body_mass_g"}),
        Plot.frame(),
    ],
}


if __name__ == "__main__":
    # Generate output files for each spec
    for key in specs:
        path = f"reference/{key}"
        if not (os.path.exists(path)):
            print(f"Generating {key}")
            op(specs[key], path=path)
        else:
            print(f"{key} already exists")
    # Serialize specs
    with open("reference/specs.pkl", "wb") as f:
        pickle.dump(specs, f)
