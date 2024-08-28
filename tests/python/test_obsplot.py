"""
Tests for Obsplot main class.
"""

import json
import tempfile

import pytest
import requests

import pyobsplot
from pyobsplot import Obsplot, Plot, obsplot
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
    return Obsplot(format="widget")


@pytest.fixture
def ow_debug():
    return Obsplot(format="widget", debug=True)


@pytest.fixture
def ow_default():
    return Obsplot(format="widget", default=default)


@pytest.fixture(scope="module")
def oj():
    oj = Obsplot(format="html")
    yield oj
    oj._jsdom_close()  # type: ignore


@pytest.fixture(scope="module")
def oj_debug():
    oj_debug = Obsplot(format="html", debug=True)
    yield oj_debug
    oj_debug._jsdom_close()  # type: ignore


@pytest.fixture(scope="module")
def oj_default():
    oj_default = Obsplot(format="html", default=default)
    yield oj_default
    oj_default._jsdom_close()  # type: ignore


@pytest.fixture(scope="module")
def oj_theme_dark():
    return Obsplot(format="html", theme="dark")


@pytest.fixture(scope="module")
def oj_theme_current():
    return Obsplot(format="html", theme="current")


class TestInit:
    def test_renderers(self, op, ow, oj):
        assert isinstance(op, pyobsplot.Obsplot)
        assert isinstance(ow, pyobsplot.Obsplot)
        assert isinstance(oj, pyobsplot.Obsplot)
        with pytest.raises(ValueError):
            Obsplot(format="foobar")  # type: ignore

    def test_debug(self, op, op_debug, ow, ow_debug, oj, oj_debug):
        assert op.debug is False
        assert op_debug.debug
        assert ow.debug is False
        assert ow_debug.debug
        assert oj.debug is False
        assert oj_debug.debug

    def test_themes(self, oj, oj_theme_dark, oj_theme_current):
        assert oj.theme == DEFAULT_THEME
        assert oj_theme_dark.theme == "dark"
        assert oj_theme_current.theme == "current"
        with pytest.raises(ValueError):
            Obsplot(theme="foobar")  # type: ignore

    @pytest.mark.filterwarnings("ignore::DeprecationWarning:ipywidgets")
    @pytest.mark.filterwarnings("ignore::DeprecationWarning:traitlets")
    def test_init(self, op, ow, oj):
        with pytest.raises(TypeError):
            op(0, x=1)
        with pytest.raises(ValueError):
            ow("foo")
        with pytest.raises(ValueError):
            oj("foo")
        with pytest.raises(TypeError):
            oj()
        spec = Plot.lineY([1, 2])  # type: ignore
        assert isinstance(op(spec), obsplot.ObsplotWidget)
        assert isinstance(ow(spec), obsplot.ObsplotWidget)
        assert oj(spec) is None

    @pytest.mark.filterwarnings("ignore::DeprecationWarning:ipywidgets")
    @pytest.mark.filterwarnings("ignore::DeprecationWarning:traitlets")
    def test_plot_plot(self, ow, oj):
        spec = Plot.lineY([1, 2])  # type: ignore
        plot = Plot.plot(spec)
        assert isinstance(plot, obsplot.ObsplotWidget)
        with pytest.raises(ValueError):
            ow(plot)
        with pytest.raises(ValueError):
            oj(plot)

    def test_default(self, ow, oj, ow_default, oj_default):
        assert ow.default == {}
        assert oj.default == {}
        assert ow_default.default == default
        assert oj_default.default == default
        wrong_default = {"x": 100}
        with pytest.raises(ValueError):
            Obsplot(format="widget", default=wrong_default)
        with pytest.raises(ValueError):
            Obsplot(format="html", default=wrong_default)

    def test_jsdom_server(self, oj):
        oj._jsdom_start()
        port = oj.jsdom_creator._port
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
        assert r.content.decode().startswith("Server error: Unexpected token")

    def test_formats(self):
        with pytest.raises(ValueError):
            Obsplot(format="foo")  # type: ignore

    def test_path_format_override_warning(self, op):
        file_path = tempfile.NamedTemporaryFile(suffix=".html")
        with pytest.warns():
            Obsplot(format="png")({}, path=file_path.name)
        with pytest.warns():
            op({}, format="png", path=file_path.name)
        with pytest.warns():
            Plot.plot({}, format="png", path=file_path.name)

    def test_path_invalid_extension(self, op):
        with pytest.raises(ValueError):
            op({}, path="foo.foo")
        with pytest.raises(ValueError):
            Plot.plot({}, path="foo.foo")

    def test_path_invalid_widget_extension(self, op):
        with pytest.raises(ValueError):
            Obsplot(format="widget")({}, path="foo.png")
        with pytest.raises(ValueError):
            op({}, format="widget", path="foo.png")
        with pytest.raises(ValueError):
            Plot.plot({}, format="widget", path="foo.png")

    def test_path_html_warning(self, op):
        html_warning = (
            "Exporting widget to HTML. If you want "
            "to output to a static HTML file, add format='html'"
        )
        file_path = tempfile.NamedTemporaryFile(suffix=".html")
        with pytest.warns(match=html_warning):
            op({}, path=file_path.name)
        with pytest.warns(match=html_warning):
            Plot.plot({}, path=file_path.name)
