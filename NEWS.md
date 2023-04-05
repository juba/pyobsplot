## pyobsplot (development version)

- Breaking change: new API, plots are now generated with a *plot generator object* created by calling `Obsplot()`. Thanks to [@fil](https://github.com/fil) for the idea.
- fix: wrong __version__value

## pyobsplot 0.2.2

- fix: plot not recreated correctly on widget value change
- fix: add watchfiles to dependencies to prevent error in Colab


## pyobsplot 0.2.1

- fix: mixing renderers in Jupyter lab moves all outputs to widgets
- Compatibility with Python 3.8


## pyobsplot 0.2.0

- New `jsdom` renderer which allows to generate plots as SVG or HTML instead of widgets.
- Update Observable Plot to 0.6.5.


## pyobsplot 0.1.3

- First released version