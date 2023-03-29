# pyobsplot


`pyobsplot` allows to use [Observable Plot](https://observablehq.com/@observablehq/plot?collection=@observablehq/plot) to create charts in Jupyter notebooks. Plots are produced as [widgets](https://ipywidgets.readthedocs.io/en/latest/index.html) from Python code with a syntax as close as possible to the JavaScript one.

It allows to do things like :

```python
import polars as pl
from pyobsplot import Obsplot, Plot

penguins = pl.read_csv("data/penguins.csv")

Obsplot({
    "grid": True,
    "color": {"legend": True},
    "marks": [
        Plot.dot(
            penguins, 
            {"x": "flipper_length_mm", "y": "body_mass_g", "fill": "species"}
        ),
        Plot.density(
            penguins, 
            {"x": "flipper_length_mm", "y": "body_mass_g", "stroke": "species"}
        )
    ]
})
```

![Sample plot screenshot](https://github.com/juba/pyobsplot/raw/main/doc/screenshots/readme_plot.png)

