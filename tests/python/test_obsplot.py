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

    def test_debug(self):
        op = Obsplot()
        assert op._debug is False
        op = Obsplot(debug=True)
        assert op._debug
        op = Obsplot(renderer="widget")
        assert op._debug is False
        op = Obsplot(renderer="widget", debug=True)
        assert op._debug
        op = Obsplot(renderer="jsdom")
        assert op._debug is False
        op = Obsplot(renderer="jsdom", debug=True)
        assert op._debug

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
        with pytest.raises(ValueError):
            ow(plot)
        with pytest.raises(ValueError):
            oj(plot)

    def test_default(self):
        ow = Obsplot(renderer="widget")
        assert ow._default == {}
        oj = Obsplot(renderer="jsdom")
        assert oj._default == {}
        default = {"width": 100, "style": {"color": "red"}}
        ow = Obsplot(renderer="widget", default=default)
        assert ow._default == default
        oj = Obsplot(renderer="jsdom", default=default)
        assert oj._default == default
        wrong_default = {"x": 100}
        with pytest.raises(ValueError):
            ow = Obsplot(renderer="widget", default=wrong_default)
        with pytest.raises(ValueError):
            oj = Obsplot(renderer="jsdom", default=wrong_default)
