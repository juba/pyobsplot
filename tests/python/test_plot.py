"""
Tests for plot.py.
"""

import pytest

from pyobsplot import plot


class TestJsModules:
    def test_plot(self):
        assert plot.Plot.dot() == {
            "pyobsplot-type": "function",
            "module": "Plot",
            "method": "dot",
            "args": (),
        }
        with pytest.raises(AttributeError):
            plot.Plot.foo()  # type: ignore

    def test_plot_args(self):
        assert plot.Plot.dot(1, "bar") == {
            "pyobsplot-type": "function",
            "module": "Plot",
            "method": "dot",
            "args": (1, "bar"),
        }
        assert plot.Plot.line([1, 2], {"x": "foo"}) == {
            "pyobsplot-type": "function",
            "module": "Plot",
            "method": "line",
            "args": ([1, 2], {"x": "foo"}),
        }
