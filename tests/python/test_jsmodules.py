"""
Tests for js_modules.
"""

import pytest

from pyobsplot import js_modules
from pyobsplot.parsing import js


class TestJsModules:
    def test_js_modules(self):
        assert js_modules.Plot.dot() == {
            "pyobsplot-type": "function",
            "module": "Plot",
            "method": "dot",
            "args": (),
        }
        assert js_modules.d3.bar() == {
            "pyobsplot-type": "function",
            "module": "d3",
            "method": "bar",
            "args": (),
        }
        assert js_modules.Math.baz() == {
            "pyobsplot-type": "function",
            "module": "Math",
            "method": "baz",
            "args": (),
        }
        assert js_modules.Math.baz() == {
            "pyobsplot-type": "function",
            "module": "Math",
            "method": "baz",
            "args": (),
        }
        with pytest.raises(AttributeError):
            js_modules.Plot.foo()

    def test_js_modules_args(self):
        assert js_modules.Plot.dot(1, "bar") == {
            "pyobsplot-type": "function",
            "module": "Plot",
            "method": "dot",
            "args": (1, "bar"),
        }
        assert js_modules.Plot.line([1, 2], {"x": "foo"}) == {
            "pyobsplot-type": "function",
            "module": "Plot",
            "method": "line",
            "args": ([1, 2], {"x": "foo"}),
        }

    def test_js_modules_kwargs(self):
        with pytest.raises(ValueError, match="kwargs must not be passed to d3\\.foo.*"):
            js_modules.d3.foo(x=1)
        with pytest.raises(ValueError, match="kwargs must not be passed to d3\\.bar.*"):
            js_modules.d3.bar(12, x=1)

    def test_js(self):
        assert js("d => d.foo") == {
            "pyobsplot-type": "js",
            "value": "d => d.foo",
        }
