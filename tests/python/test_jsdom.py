"""
Tests for Obsplot jsdom file output.
"""

import pytest
import io
import pickle

from pyobsplot import Obsplot, Plot


@pytest.fixture(scope="module")
def oj():
    oj = Obsplot(renderer="jsdom")
    yield oj
    oj.close()  # type: ignore


@pytest.fixture(scope="module")
def specs():
    with open("tests/python/reference/specs.pkl", "rb") as f:
        specs = pickle.load(f)
    return specs


class TestSpecs:
    def test_jsdom_plots(self, oj, specs):
        results = dict()
        for k, spec in specs.items():
            out = io.StringIO()
            oj(spec, path=out)
            with open(f"tests/python/reference/{k}", "r") as f:
                results[k] = out.getvalue() == f.read()
            out.close()
        print(results)
        assert all(results)
