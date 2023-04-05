"""
Tests for Obsplot main class.
"""

import pytest

import pyobsplot
from pyobsplot import Obsplot


class TestWidget:
    def test_renderers(self):
        op = Obsplot()
        ow = Obsplot(renderer="widget")
        oj = Obsplot(renderer="jsdom")
        assert type(op) == pyobsplot.obsplot.ObsplotWidgetCreator
        assert type(ow) == pyobsplot.obsplot.ObsplotWidgetCreator
        assert type(oj) == pyobsplot.obsplot.ObsplotJsdomCreator
        with pytest.raises(ValueError):
            Obsplot(renderer="foobar")

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
