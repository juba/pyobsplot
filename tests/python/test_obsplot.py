"""
Tests for Obsplot main class.
"""

import pytest
import requests
import json

import pyobsplot
from pyobsplot import Obsplot, Plot
from pyobsplot.utils import DEFAULT_THEME

default = {"width": 100, "style": {"color": "red"}}


@pytest.fixture
def op():
    return Obsplot()


@pytest.fixture
def op_debug():
    return Obsplot(debug=True)


@pytest.fixture
def ow():
    return Obsplot(renderer="widget")


@pytest.fixture
def ow_debug():
    return Obsplot(renderer="widget", debug=True)


@pytest.fixture
def ow_default():
    return Obsplot(renderer="widget", default=default)


@pytest.fixture(scope="module")
def oj():
    oj = Obsplot(renderer="jsdom")
    yield oj
    oj.close()  # type: ignore


@pytest.fixture(scope="module")
def oj_debug():
    oj_debug = Obsplot(renderer="jsdom", debug=True)
    yield oj_debug
    oj_debug.close()  # type: ignore


@pytest.fixture(scope="module")
def oj_default():
    oj_default = Obsplot(renderer="jsdom", default=default)
    yield oj_default
    oj_default.close()  # type: ignore


@pytest.fixture(scope="module")
def oj_theme_dark():
    return Obsplot(renderer="jsdom", theme="dark")


@pytest.fixture(scope="module")
def oj_theme_current():
    return Obsplot(renderer="jsdom", theme="current")


class TestInit:
    def test_renderers(self, op, ow, oj):
        assert isinstance(op, pyobsplot.obsplot.ObsplotWidgetCreator)
        assert isinstance(ow, pyobsplot.obsplot.ObsplotWidgetCreator)
        assert isinstance(oj, pyobsplot.obsplot.ObsplotJsdomCreator)
        with pytest.raises(ValueError):
            Obsplot(renderer="foobar")

    def test_debug(self, op, op_debug, ow, ow_debug, oj, oj_debug):
        assert op._debug is False
        assert op_debug._debug
        assert ow._debug is False
        assert ow_debug._debug
        assert oj._debug is False
        assert oj_debug._debug

    def test_themes(self, oj, oj_theme_dark, oj_theme_current):
        assert oj._theme == DEFAULT_THEME
        assert oj_theme_dark._theme == "dark"
        assert oj_theme_current._theme == "current"
        with pytest.raises(ValueError):
            Obsplot(theme="foobar")

    @pytest.mark.filterwarnings("ignore::DeprecationWarning:ipywidgets")
    @pytest.mark.filterwarnings("ignore::DeprecationWarning:traitlets")
    def test_init(self, op, ow, oj):
        with pytest.raises(ValueError):
            op(0, x=1)
        with pytest.raises(ValueError):
            ow("foo")
        with pytest.raises(ValueError):
            oj("foo")
        with pytest.raises(ValueError):
            oj()
        spec = Plot.lineY([1, 2])  # type: ignore
        assert isinstance(op(spec), pyobsplot.obsplot.ObsplotWidget)
        assert isinstance(ow(spec), pyobsplot.obsplot.ObsplotWidget)
        assert oj(spec) is None

    @pytest.mark.filterwarnings("ignore::DeprecationWarning:ipywidgets")
    @pytest.mark.filterwarnings("ignore::DeprecationWarning:traitlets")
    def test_plot_plot(self, ow, oj):
        spec = Plot.lineY([1, 2])  # type: ignore
        plot = Plot.plot(spec)
        assert isinstance(plot, pyobsplot.obsplot.ObsplotWidget)
        with pytest.raises(ValueError):
            ow(plot)
        with pytest.raises(ValueError):
            oj(plot)

    def test_default(self, ow, oj, ow_default, oj_default):
        assert ow._default == {}
        assert oj._default == {}
        assert ow_default._default == default
        assert oj_default._default == default
        wrong_default = {"x": 100}
        with pytest.raises(ValueError):
            Obsplot(renderer="widget", default=wrong_default)
        with pytest.raises(ValueError):
            Obsplot(renderer="jsdom", default=wrong_default)

    def test_jsdom_server(self, oj):
        port = oj._port
        assert port > 1024 and port <= 65535

        url = f"http://localhost:{port}"

        # /status request
        r = requests.get(url + "/status")
        assert r.text == "pyobsplot"

        # correct /plot request
        req_data = json.dumps(
            {
                "theme": "light",
                "spec": {
                    "data": [],
                    "code": {
                        "marks": [
                            {
                                "pyobsplot-type": "function",
                                "module": "Plot",
                                "method": "auto",
                                "args": [],
                            }
                        ]
                    },
                    "debug": False,
                },
            }
        )
        r = requests.post(url + "/plot", data=req_data)
        assert r.status_code == 200
        assert (
            r.content.decode()
            == '<pre style="color: rgb(221, 51, 51); padding: .5em 1em;">⚠ Error: must specify x or y</pre>'  # noqa: E501
        )

        # bad /plot request
        r = requests.post(url + "/plot", data="this is no valid json")
        assert r.status_code == 500
        assert (
            r.content.decode()
            == "Server error: Unexpected token h in JSON at position 1."
        )
