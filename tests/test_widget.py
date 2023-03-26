"""
Tests for widget.
"""

import pytest

from pyobsplot import Obsplot


class TestWidget:
    def test_widget_init(self):
        with pytest.raises(ValueError):
            Obsplot(0, x=1)
        with pytest.raises(ValueError):
            Obsplot("foo")

        ## Commented out due to traitlets DeprecationWarnings
        # assert Obsplot(x=1, y="foo").spec == {"x": 1, "y": "foo"}
        # assert Obsplot({"x": 1, "y": "foo"}).spec == {"x": 1, "y": "foo"}
        # assert Obsplot(spec={"x": 1, "y": "foo"}).spec == {"x": 1, "y": "foo"}
