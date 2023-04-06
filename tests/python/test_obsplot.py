"""
Tests for Obsplot main class.
"""

import pytest

import pyobsplot
from pyobsplot import Obsplot, Plot


class TestInit:
    def test_renderers(self):
        op = Obsplot()
        ow = Obsplot(renderer="widget")
        oj = Obsplot(renderer="jsdom")
        assert isinstance(op, pyobsplot.obsplot.ObsplotWidgetCreator)
        assert isinstance(ow, pyobsplot.obsplot.ObsplotWidgetCreator)
        assert isinstance(oj, pyobsplot.obsplot.ObsplotJsdomCreator)
        with pytest.raises(ValueError):
            Obsplot(renderer="foobar")

    @pytest.mark.filterwarnings("ignore::DeprecationWarning:ipywidgets")
    def test_init(self):
        op = Obsplot()
        ow = Obsplot(renderer="widget")
        oj = Obsplot(renderer="jsdom")
        with pytest.raises(ValueError):
            op(0, x=1)
        with pytest.raises(ValueError):
            ow("foo")
        with pytest.raises(ValueError):
            oj("foo")
        with pytest.raises(ValueError):
            oj()
        spec = Plot.lineY([1, 2])
        assert isinstance(op(spec), pyobsplot.obsplot.ObsplotWidget)
        assert isinstance(ow(spec), pyobsplot.obsplot.ObsplotWidget)
        assert oj(spec) is None

    @pytest.mark.filterwarnings("ignore::DeprecationWarning:ipywidgets")
    def test_plot_plot(self):
        spec = Plot.lineY([1, 2])
        ow = Obsplot(renderer="widget")
        oj = Obsplot(renderer="jsdom")
        plot = Plot.plot(spec)
        assert isinstance(plot, pyobsplot.obsplot.ObsplotWidget)
        ow_plot = ow(plot)
        assert isinstance(ow_plot, pyobsplot.obsplot.ObsplotWidget)
        assert ow_plot.spec == plot.spec
        with pytest.raises(ValueError):
            oj(plot)
