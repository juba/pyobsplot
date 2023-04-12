"""
Tests for jsmodules.
"""

import pytest

from pyobsplot import jsmodules
from pyobsplot.parsing import js


class TestJsModules:
    def test_js_modules(self):
        assert jsmodules.Plot.foo() == {
            "pyobsplot-type": "function",
            "module": "Plot",
            "method": "foo",
            "args": (),
        }
        assert jsmodules.d3.bar() == {
            "pyobsplot-type": "function",
            "module": "d3",
            "method": "bar",
            "args": (),
        }
        assert jsmodules.Math.baz() == {
            "pyobsplot-type": "function",
            "module": "Math",
            "method": "baz",
            "args": (),
        }
        assert jsmodules.Math.baz() == {
            "pyobsplot-type": "function",
            "module": "Math",
            "method": "baz",
            "args": (),
        }

    def test_js_modules_args(self):
        assert jsmodules.Plot.foo(1, "bar") == {
            "pyobsplot-type": "function",
            "module": "Plot",
            "method": "foo",
            "args": (1, "bar"),
        }
        assert jsmodules.Plot.foo([1, 2], {"x": "foo"}) == {
            "pyobsplot-type": "function",
            "module": "Plot",
            "method": "foo",
            "args": ([1, 2], {"x": "foo"}),
        }

    def test_js_modules_kwargs(self):
        with pytest.raises(ValueError, match="kwargs must not be passed to d3\\.foo.*"):
            jsmodules.d3.foo(x=1)
        with pytest.raises(ValueError, match="kwargs must not be passed to d3\\.bar.*"):
            jsmodules.d3.bar(12, x=1)

    def test_js(self):
        assert js("d => d.foo") == {
            "pyobsplot-type": "js",
            "value": "d => d.foo",
        }