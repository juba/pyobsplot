"""
Tests for Obsplot main class.
"""

import pytest

from pyobsplot import Obsplot
from pyobsplot.utils import default_renderer, available_renderers


class TestWidget:
    def test_init(self):
        with pytest.raises(ValueError):
            Obsplot(0, x=1)
        with pytest.raises(ValueError):
            Obsplot("foo")

    def test_renderers(self):
        assert Obsplot.renderer == default_renderer
        Obsplot.set_renderer("jsdom")
        assert Obsplot.renderer == "jsdom"
        Obsplot.set_renderer("widget")
        assert Obsplot.renderer == "widget"
        with pytest.raises(ValueError):
            Obsplot.set_renderer("nawak")
