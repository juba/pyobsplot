## pyobsplot 0.3.5-dev

- Update Observable Plot to 0.6.7 (tooltips ! interactions !)
- Update apache-arrow to 12.0.0
- Update anywidget to 0.3.0


## pyobsplot 0.3.4

- Add small padding around figure outputs for jsdom renderer to improve presentation over non-white backgrounds.
- Update Observable Plot to 0.6.6.


## pyobsplot 0.3.3

- `jsdom` renderer now uses a local http server instead of calling a script at each invocation, greatly improving rendering speed.
- Autocompletion of Plot methods should now be working in IDEs.
- Ensure that the needed version of the npm package is run if jsdom renderer is used.
- Debug mode also works with `jsdom` renderer.
- Plot generator objects now have correct `__repr__` methods.
- Update anywidget to 0.2.3.
- Fix: "Exception not rethrown" errors in pytest.


## pyobsplot 0.3.2

- Add ability to specify some default spec values to plot generator objects.
- `range` objects are correctly serialized as lists for `jsdom` renderer.
- Fix: don't add styles to svg or html output if these styles are already present.
- Fix: jsdom renderer not working on Windows.


## pyobsplot 0.3.1

- It is now possible to use `Plot.plot()` directly when creating a plot with default settings.Thanks to [@fil](https://github.com/fil) for the idea.
- GeoJson data passed as `string` instead of `dict` is serialized correctly.
- Add debug mode to output.
 

## pyobsplot 0.3.0

- Breaking change: new API, plots are now generated with a *plot generator object* created by calling `Obsplot()`. Thanks to [@fil](https://github.com/fil) for the idea.
- Fix: wrong `__version__` value.


## pyobsplot 0.2.2

- Fix: plot not recreated correctly on widget value change.
- Fix: add watchfiles to dependencies to prevent error in Colab.


## pyobsplot 0.2.1

- Fix: mixing renderers in Jupyter lab moves all outputs to widgets.
- Compatibility with Python 3.8.


## pyobsplot 0.2.0

- New `jsdom` renderer which allows to generate plots as SVG or HTML instead of widgets.
- Update Observable Plot to 0.6.5.


## pyobsplot 0.1.3

- First released version.