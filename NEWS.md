## pyobsplot (development version)

- Add ability to specify some default spec values to plot generator objects.


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