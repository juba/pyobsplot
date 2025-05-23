## pyobsplot 0.5.4


## pyobsplot 0.5.3.2

-   Installing the package with `pip install pyobsplot` now does not install the `typst` dependency anymore. To install typst and allow to use all the renderers, you have to install with `pip install pyobsplot[typst]`. This change has been made so that `pyobsplot` (with the widget renderer) could be used in pyodide-based environments like JupyterLite and Marimo.

## pyobsplot 0.5.2

-   Update Observable Plot to 0.6.17

## pyobsplot 0.5.1

-   `Plot.plot()` performance should now be equivalent to the one of a generator object
-   New shortcut syntax `Plot.line(...).plot()` is now available (#18, thanks @harrylojames)
-   Bugfix: typst error with certain decimal padding values.

## pyobsplot 0.5.0

### Breaking changes

-   The plot generator API has been changed. Generators are no more defined with a `renderer` argument, a `format` is specified instead. This format can either be `widget`, `html`, `svg` or `png`. So `renderer="widget"` is replaced by `format="widget"` (which is the default), whereas `renderer="jsdom"` is replaced by `format="html"` or one of the new `format="svg"` and `format="png"`.
-   The "kwargs" alternative syntax is now deprecated and will generate errors. Plots must be defined either by passing a specification dictionary, or a call to a `Plot.xxx` method.

### Other changes

-   Plots can now be generated in "svg" and "png", and saved as "svg", "png" or "pdf".
    This is done by converting figures using [typst](https://typst.app). Many thanks to
    @wirhabenzeit and @harrylojames for the idea, the underlying code and the feedback.
-   Update Observable Plot to 0.6.16
-   Migrate project management from hatch to uv

## pyobsplot 0.4.2

-   Fix `jsdom` renderer file saving encoding (#22, @harrylojames)
-   Update Observable Plot to 0.6.13
-   Migrate build system from poetry to hatch
-   Update pyarrow and apache-arrow to 15.0.0 and remove data frame conversion to 32bits data types before serialization

## pyobsplot 0.4.1

-   Plots generated by the `widget` renderer can now be saved to HTML files
-   Move required Python version to 3.9
-   Update pyarrow to 13.0.0

## pyobsplot 0.4.0

-   Plots generated by the `jsdom` renderer can now be saved to HTML or SVG files
-   Update Observable Plot to 0.6.11
-   Update anywidget to 0.6.5

## pyobsplot 0.3.8

-   Update Observable Plot to 0.6.10
-   Add styling for titles, subtitles and captions
-   Update anywidget to 0.6.3

## pyobsplot 0.3.7

-   Update Observable Plot to 0.6.9
-   Update anywidget to 0.6.1

## pyobsplot 0.3.6

-   Fix UnicodeDecodeError with widget renderer on Windows (#17, thanks @harrylojames)
-   Timestamp and datetime dataframe columns are now converted to JavaScript Date (#19, thanks @harrylojames)
-   Update anywidget to 0.4.3

## pyobsplot 0.3.5

-   Update Observable Plot to 0.6.8 (tooltips and interactions in widget renderer)
-   Add light/dark/current modes
-   Update apache-arrow to 12.0.0
-   Update anywidget to 0.4.2

## pyobsplot 0.3.4

-   Add small padding around figure outputs for jsdom renderer to improve presentation over non-white backgrounds.
-   Update Observable Plot to 0.6.6.

## pyobsplot 0.3.3

-   `jsdom` renderer now uses a local http server instead of calling a script at each invocation, greatly improving rendering speed.
-   Autocompletion of Plot methods should now be working in IDEs.
-   Ensure that the needed version of the npm package is run if jsdom renderer is used.
-   Debug mode also works with `jsdom` renderer.
-   Plot generator objects now have correct `__repr__` methods.
-   Update anywidget to 0.2.3.
-   Fix: "Exception not rethrown" errors in pytest.

## pyobsplot 0.3.2

-   Add ability to specify some default spec values to plot generator objects.
-   `range` objects are correctly serialized as lists for `jsdom` renderer.
-   Fix: don't add styles to svg or html output if these styles are already present.
-   Fix: jsdom renderer not working on Windows.

## pyobsplot 0.3.1

-   It is now possible to use `Plot.plot()` directly when creating a plot with default settings.Thanks to [@fil](https://github.com/fil) for the idea.
-   GeoJson data passed as `string` instead of `dict` is serialized correctly.
-   Add debug mode to output.

## pyobsplot 0.3.0

-   Breaking change: new API, plots are now generated with a _plot generator object_ created by calling `Obsplot()`. Thanks to [@fil](https://github.com/fil) for the idea.
-   Fix: wrong `__version__` value.

## pyobsplot 0.2.2

-   Fix: plot not recreated correctly on widget value change.
-   Fix: add watchfiles to dependencies to prevent error in Colab.

## pyobsplot 0.2.1

-   Fix: mixing renderers in Jupyter lab moves all outputs to widgets.
-   Compatibility with Python 3.8.

## pyobsplot 0.2.0

-   New `jsdom` renderer which allows to generate plots as SVG or HTML instead of widgets.
-   Update Observable Plot to 0.6.5.

## pyobsplot 0.1.3

-   First released version.
