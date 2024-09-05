"""
Tests for js_modules.py.
"""

import pytest

from pyobsplot import js_modules
from pyobsplot.parsing import js


class TestJsModules:
    def test_js_modules(self):
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
